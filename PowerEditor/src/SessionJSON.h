#pragma once
#include "Parameters.h"
#include "json/json.hpp"
#include <windows.h>
#include <string>
#include <vector>

using json = nlohmann::json;

// Helper functions for UTF-8 conversion
inline std::string toUtf8(const std::wstring& wstr) {
    if (wstr.empty()) return "";
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), NULL, 0, NULL, NULL);
    std::string str(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), &str[0], size_needed, NULL, NULL);
    return str;
}

inline std::wstring toWide(const std::string& str) {
    if (str.empty()) return L"";
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), NULL, 0);
    std::wstring wstr(size_needed, 0);
    MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), &wstr[0], size_needed);
    return wstr;
}

inline void to_json(json& j, const Position& p) {
    j = json{
        {"firstVisibleLine", p._firstVisibleLine},
        {"startPos", p._startPos},
        {"endPos", p._endPos},
        {"xOffset", p._xOffset},
        {"selMode", p._selMode},
        {"scrollWidth", p._scrollWidth},
        {"offset", p._offset},
        {"wrapCount", p._wrapCount}
    };
}

inline void from_json(const json& j, Position& p) {
    if(j.contains("firstVisibleLine")) j.at("firstVisibleLine").get_to(p._firstVisibleLine);
    if(j.contains("startPos")) j.at("startPos").get_to(p._startPos);
    if(j.contains("endPos")) j.at("endPos").get_to(p._endPos);
    if(j.contains("xOffset")) j.at("xOffset").get_to(p._xOffset);
    if(j.contains("selMode")) j.at("selMode").get_to(p._selMode);
    if(j.contains("scrollWidth")) j.at("scrollWidth").get_to(p._scrollWidth);
    if(j.contains("offset")) j.at("offset").get_to(p._offset);
    if(j.contains("wrapCount")) j.at("wrapCount").get_to(p._wrapCount);
}

inline void to_json(json& j, const MapPosition& p) {
    j = json{
        {"firstVisibleDisplayLine", p._firstVisibleDisplayLine},
        {"firstVisibleDocLine", p._firstVisibleDocLine},
        {"lastVisibleDocLine", p._lastVisibleDocLine},
        {"nbLine", p._nbLine},
        {"higherPos", p._higherPos},
        {"width", p._width},
        {"height", p._height},
        {"wrapIndentMode", p._wrapIndentMode},
        {"KByteInDoc", p._KByteInDoc},
        {"isWrap", p._isWrap}
    };
}

inline void from_json(const json& j, MapPosition& p) {
    if(j.contains("firstVisibleDisplayLine")) j.at("firstVisibleDisplayLine").get_to(p._firstVisibleDisplayLine);
    if(j.contains("firstVisibleDocLine")) j.at("firstVisibleDocLine").get_to(p._firstVisibleDocLine);
    if(j.contains("lastVisibleDocLine")) j.at("lastVisibleDocLine").get_to(p._lastVisibleDocLine);
    if(j.contains("nbLine")) j.at("nbLine").get_to(p._nbLine);
    if(j.contains("higherPos")) j.at("higherPos").get_to(p._higherPos);
    if(j.contains("width")) j.at("width").get_to(p._width);
    if(j.contains("height")) j.at("height").get_to(p._height);
    if(j.contains("wrapIndentMode")) j.at("wrapIndentMode").get_to(p._wrapIndentMode);
    if(j.contains("KByteInDoc")) j.at("KByteInDoc").get_to(p._KByteInDoc);
    if(j.contains("isWrap")) j.at("isWrap").get_to(p._isWrap);
}

inline void to_json(json& j, const sessionFileInfo& s) {
    // Serialize base class
    to_json(j, static_cast<const Position&>(s));
    
    j["fileName"] = toUtf8(s._fileName);
    j["langName"] = toUtf8(s._langName);
    j["marks"] = s._marks;
    j["foldStates"] = s._foldStates;
    j["encoding"] = s._encoding;
    j["isUserReadOnly"] = s._isUserReadOnly;
    j["isMonitoring"] = s._isMonitoring;
    j["individualTabColour"] = s._individualTabColour;
    j["isRTL"] = s._isRTL;
    j["isPinned"] = s._isPinned;
    j["isUntitledTabRenamed"] = s._isUntitledTabRenamed;
    j["backupFilePath"] = toUtf8(s._backupFilePath);
    j["originalFileLastModifTimestamp"] = {
        {"low", s._originalFileLastModifTimestamp.dwLowDateTime},
        {"high", s._originalFileLastModifTimestamp.dwHighDateTime}
    };
    j["mapPos"] = s._mapPos;
}

inline void from_json(const json& j, sessionFileInfo& s) {
    from_json(j, static_cast<Position&>(s));
    
    if(j.contains("fileName")) s._fileName = toWide(j.at("fileName").get<std::string>());
    if(j.contains("langName")) s._langName = toWide(j.at("langName").get<std::string>());
    if(j.contains("marks")) s._marks = j.at("marks").get<std::vector<size_t>>();
    if(j.contains("foldStates")) s._foldStates = j.at("foldStates").get<std::vector<size_t>>();
    if(j.contains("encoding")) j.at("encoding").get_to(s._encoding);
    if(j.contains("isUserReadOnly")) j.at("isUserReadOnly").get_to(s._isUserReadOnly);
    if(j.contains("isMonitoring")) j.at("isMonitoring").get_to(s._isMonitoring);
    if(j.contains("individualTabColour")) j.at("individualTabColour").get_to(s._individualTabColour);
    if(j.contains("isRTL")) j.at("isRTL").get_to(s._isRTL);
    if(j.contains("isPinned")) j.at("isPinned").get_to(s._isPinned);
    if(j.contains("isUntitledTabRenamed")) j.at("isUntitledTabRenamed").get_to(s._isUntitledTabRenamed);
    if(j.contains("backupFilePath")) s._backupFilePath = toWide(j.at("backupFilePath").get<std::string>());
    
    if(j.contains("originalFileLastModifTimestamp")) {
        auto& ts = j.at("originalFileLastModifTimestamp");
        if(ts.contains("low")) ts.at("low").get_to(s._originalFileLastModifTimestamp.dwLowDateTime);
        if(ts.contains("high")) ts.at("high").get_to(s._originalFileLastModifTimestamp.dwHighDateTime);
    }
    
    if(j.contains("mapPos")) j.at("mapPos").get_to(s._mapPos);
}

inline void to_json(json& j, const Session& s) {
    j = json{
        {"activeView", s._activeView},
        {"activeMainIndex", s._activeMainIndex},
        {"activeSubIndex", s._activeSubIndex},
        {"includeFileBrowser", s._includeFileBrowser},
        {"fileBrowserSelectedItem", toUtf8(s._fileBrowserSelectedItem)},
        {"mainViewFiles", s._mainViewFiles},
        {"subViewFiles", s._subViewFiles}
    };
    
    std::vector<std::string> roots;
    for(const auto& root : s._fileBrowserRoots) {
        roots.push_back(toUtf8(root));
    }
    j["fileBrowserRoots"] = roots;
}

inline void from_json(const json& j, Session& s) {
    if(j.contains("activeView")) j.at("activeView").get_to(s._activeView);
    if(j.contains("activeMainIndex")) j.at("activeMainIndex").get_to(s._activeMainIndex);
    if(j.contains("activeSubIndex")) j.at("activeSubIndex").get_to(s._activeSubIndex);
    if(j.contains("includeFileBrowser")) j.at("includeFileBrowser").get_to(s._includeFileBrowser);
    if(j.contains("fileBrowserSelectedItem")) s._fileBrowserSelectedItem = toWide(j.at("fileBrowserSelectedItem").get<std::string>());
    if(j.contains("mainViewFiles")) s._mainViewFiles = j.at("mainViewFiles").get<std::vector<sessionFileInfo>>();
    if(j.contains("subViewFiles")) s._subViewFiles = j.at("subViewFiles").get<std::vector<sessionFileInfo>>();
    
    if(j.contains("fileBrowserRoots")) {
        auto roots = j.at("fileBrowserRoots").get<std::vector<std::string>>();
        s._fileBrowserRoots.clear();
        for(const auto& root : roots) {
            s._fileBrowserRoots.push_back(toWide(root));
        }
    }
}
