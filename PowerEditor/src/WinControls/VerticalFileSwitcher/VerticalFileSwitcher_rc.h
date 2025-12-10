// This file is part of Notepad++ project
// Copyright (C)2021 Don HO <don.h@free.fr>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// at your option any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.


#pragma once

#define	IDD_DOCLIST		3000
#define	IDC_LIST_DOCLIST    (IDD_DOCLIST + 1)

// List View Column ID
#define	IDC_CLMNNAME_VFS      (IDD_DOCLIST + 2)
#define	IDC_CLMNEXT_VFS       (IDD_DOCLIST + 3)  
#define	IDC_CLMNCATEGORY_VFS  (IDD_DOCLIST + 4)  // Category Column ID


// Category Menu ID Range
#define	CATEGORY_MENU_START  3060
#define	CATEGORY_MENU_END    3070
#define	CATEGORY_MENU_ID     3059

// Category Button ID Range
#define	CATEGORY_BUTTON_START  3070
#define	CATEGORY_BUTTON_END    3080

// Font Size Menu ID
#define	FONTSIZE_6           3080
#define	FONTSIZE_8           3081
#define	FONTSIZE_10          3082
#define	FONTSIZE_12          3083
#define	FONTSIZE_14          3084
#define	FONTSIZE_16          3085  // 添加缺失的定义

// Tab Color菜单ID
#define	TAB_COLOR_MENU_START  3090
#define	TAB_COLOR_MENU_END    3100
#define	TAB_COLOR_MENU_ID     3089

// Settings Button ID
#define	IDC_SETTINGS_BUTTON_VFS 3099

// Settings Menu ID
#define	IDM_SETTINGS_VFS 3100

// Edit Category JSON Menu ID
#define	IDM_EDIT_CATEGORY_JSON 3101

// Close Current File Menu ID
#define	IDM_DOCLIST_CLOSE_CURRENT 3102

// Settings Dialog ID
#define	IDD_DOCLIST_SETTINGS 3050
// Input Dialog ID
#define IDD_DOCLIST_INPUT_DLG 3051

// Settings Dialog Control ID
#define	IDC_FONTSIZE_SLIDER 3051
#define	IDC_FONTSIZE_DISPLAY 3052
#define	IDC_CATEGORY_LIST 3053
#define	IDC_ADD_CATEGORY 3054
#define	IDC_DELETE_CATEGORY 3055
#define	IDC_RENAME_CATEGORY 3056
