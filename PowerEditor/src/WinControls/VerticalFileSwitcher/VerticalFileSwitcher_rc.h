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
#define	IDC_FONTSIZE_STATIC_VFS (IDD_DOCLIST + 2)  // 修改为避免冲突的名称
#define	IDC_FONTSIZE_COMBO_VFS  (IDD_DOCLIST + 3)  // 修改为避免冲突的名称

// 分类菜单ID范围
#define	CATEGORY_MENU_START  (IDD_DOCLIST + 100)
#define	CATEGORY_MENU_END    (CATEGORY_MENU_START + 50)
#define	CATEGORY_MENU_ID     (IDD_DOCLIST + 99)

// 分类按钮ID范围
#define	CATEGORY_BUTTON_START  (IDD_DOCLIST + 150)
#define	CATEGORY_BUTTON_END    (CATEGORY_BUTTON_START + 50)

// 字体大小菜单ID
#define	FONTSIZE_6           (IDD_DOCLIST + 200)
#define	FONTSIZE_8           (IDD_DOCLIST + 201)
#define	FONTSIZE_10          (IDD_DOCLIST + 202)
#define	FONTSIZE_12          (IDD_DOCLIST + 203)
#define	FONTSIZE_14          (IDD_DOCLIST + 204)
#define	FONTSIZE_16          (IDD_DOCLIST + 205)  // 添加缺失的定义

// 标签颜色菜单ID
#define	TAB_COLOR_MENU_START  (IDD_DOCLIST + 250)
#define	TAB_COLOR_MENU_END    (TAB_COLOR_MENU_START + 10)
#define	TAB_COLOR_MENU_ID     (IDD_DOCLIST + 249)
