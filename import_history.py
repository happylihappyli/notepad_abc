import os
import shutil
import xml.etree.ElementTree as ET
import json
import sys

# Define paths
notepadpp_config_dir = os.path.join(os.environ['APPDATA'], 'Notepad++')
notepadpp_session_xml = os.path.join(notepadpp_config_dir, 'session.xml')

notepadabc_config_dir = os.path.join(os.environ['APPDATA'], 'Notepad_abc')
notepadabc_session_json = os.path.join(notepadabc_config_dir, 'session.json')
notepadabc_backup_dir = os.path.join(notepadabc_config_dir, 'backup')

def parse_bool(value):
    return value == "yes"

def parse_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def parse_file_node(file_node, dest_backup_dir):
    file_info = {
        # Position fields
        "firstVisibleLine": parse_int(file_node.get('firstVisibleLine')),
        "startPos": parse_int(file_node.get('startPos')),
        "endPos": parse_int(file_node.get('endPos')),
        "xOffset": parse_int(file_node.get('xOffset')),
        "selMode": parse_int(file_node.get('selMode')),
        "scrollWidth": parse_int(file_node.get('scrollWidth')),
        "offset": parse_int(file_node.get('offset')),
        "wrapCount": parse_int(file_node.get('wrapCount')),
        
        # sessionFileInfo fields
        "fileName": file_node.get('filename', ''),
        "langName": file_node.get('lang', ''),
        "encoding": parse_int(file_node.get('encoding'), -1),
        "isUserReadOnly": parse_bool(file_node.get('userReadOnly')),
        "isMonitoring": False, # Default
        "individualTabColour": parse_int(file_node.get('tabColourId'), -1),
        "isRTL": parse_bool(file_node.get('RTL')),
        "isPinned": parse_bool(file_node.get('tabPinned')),
        "isUntitledTabRenamed": parse_bool(file_node.get('untitleTabRenamed')),
        
        "originalFileLastModifTimestamp": {
            "low": parse_int(file_node.get('originalFileLastModifTimestamp')),
            "high": parse_int(file_node.get('originalFileLastModifTimestampHigh'))
        },
        
        "mapPos": {
            "firstVisibleDisplayLine": parse_int(file_node.get('mapFirstVisibleDisplayLine')),
            "firstVisibleDocLine": parse_int(file_node.get('mapFirstVisibleDocLine')),
            "lastVisibleDocLine": parse_int(file_node.get('mapLastVisibleDocLine')),
            "nbLine": parse_int(file_node.get('mapNbLine')),
            "higherPos": parse_int(file_node.get('mapHigherPos')),
            "width": parse_int(file_node.get('mapWidth')),
            "height": parse_int(file_node.get('mapHeight')),
            "wrapIndentMode": parse_int(file_node.get('mapWrapIndentMode')),
            "KByteInDoc": parse_int(file_node.get('mapKByteInDoc')),
            "isWrap": parse_bool(file_node.get('mapIsWrap'))
        }
    }

    # Handle Marks
    marks = []
    for mark in file_node.findall('Mark'):
        marks.append(parse_int(mark.get('line')))
    file_info["marks"] = marks

    # Handle Folds
    folds = []
    for fold in file_node.findall('Fold'):
        folds.append(parse_int(fold.get('line')))
    file_info["foldStates"] = folds

    # Handle Backup
    backup_path = file_node.get('backupFilePath')
    if backup_path and os.path.exists(backup_path):
        backup_fname = os.path.basename(backup_path)
        new_backup_path = os.path.join(dest_backup_dir, backup_fname)
        
        if not os.path.exists(new_backup_path):
            try:
                shutil.copy2(backup_path, new_backup_path)
                print(f"Copied backup: {backup_path} -> {new_backup_path}")
            except Exception as e:
                print(f"Failed to copy backup {backup_path}: {e}")
        
        file_info["backupFilePath"] = new_backup_path
    else:
        file_info["backupFilePath"] = ""

    return file_info

def export_list_to_markdown(session_data, md_file_path):
    try:
        with open(md_file_path, 'a', encoding='utf-8') as f:
            f.write("\n\n## Notepad++ 最近打开文件列表\n\n")
            for file_info in session_data.get("mainViewFiles", []):
                f.write(f"- {file_info['fileName']}\n")
            for file_info in session_data.get("subViewFiles", []):
                f.write(f"- {file_info['fileName']}\n")
        print(f"Successfully exported file list to {md_file_path}")
    except Exception as e:
        print(f"Error exporting to markdown: {e}")

def import_session_to_json():
    print(f"Reading from: {notepadpp_session_xml}")
    print(f"Writing to: {notepadabc_session_json}")
    
    if not os.path.exists(notepadpp_session_xml):
        print("Notepad++ session.xml not found.")
        return

    # Create backup directory if it doesn't exist
    os.makedirs(notepadabc_backup_dir, exist_ok=True)

    try:
        tree = ET.parse(notepadpp_session_xml)
        root = tree.getroot()
        session_node = root.find('Session')
        
        active_view = 0
        active_main_index = 0
        active_sub_index = 0
        
        if session_node is not None:
            active_view = parse_int(session_node.get('activeView'))
            main_view_node = session_node.find('mainView')
            if main_view_node is not None:
                active_main_index = parse_int(main_view_node.get('activeIndex'))
            sub_view_node = session_node.find('subView')
            if sub_view_node is not None:
                active_sub_index = parse_int(sub_view_node.get('activeIndex'))
        
        session_data = {
            "activeView": active_view,
            "activeMainIndex": active_main_index,
            "activeSubIndex": active_sub_index,
            "includeFileBrowser": False,
            "fileBrowserSelectedItem": "",
            "mainViewFiles": [],
            "subViewFiles": [],
            "fileBrowserRoots": []
        }
        
        # Parse main view files
        for file_node in root.findall("./Session/mainView/File"):
            session_data["mainViewFiles"].append(parse_file_node(file_node, notepadabc_backup_dir))
            
        # Parse sub view files
        for file_node in root.findall("./Session/subView/File"):
            session_data["subViewFiles"].append(parse_file_node(file_node, notepadabc_backup_dir))
            
        # Write to session.json
        with open(notepadabc_session_json, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4, ensure_ascii=False)
        print("Successfully wrote session.json")

        # Export to markdown
        md_file = r"e:\GitHub3\cpp\notepad_abc\使用说明.md"
        export_list_to_markdown(session_data, md_file)

    except Exception as e:
        print(f"Error processing session files: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import_session_to_json()
