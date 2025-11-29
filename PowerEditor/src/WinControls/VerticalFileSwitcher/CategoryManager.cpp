// 分类管理器实现文件

#include "CategoryManager.h"
#include <fstream>
#include <algorithm>
#include <windows.h>
#include <shlwapi.h> // 包含 PathRemoveFileSpecW, PathCombineW 和 PathCanonicalizeW 的声明
#pragma comment(lib, "shlwapi.lib") // 链接 shlwapi 库



CategoryManager::CategoryManager() {
    // 默认配置文件路径
    m_configPath = L"..\\bin\\categories.json";
    
    // 添加调试信息
    std::wstring debugMsg = L"CategoryManager: 构造函数调用，初始配置路径: " + m_configPath + L"\n";
    OutputDebugStringW(debugMsg.c_str());
}

/**
 * @brief 初始化分类管理器
 */
void CategoryManager::initialize(const std::wstring& configPath) {
    if (!configPath.empty()) {
        m_configPath = configPath;
    }
    
    // 调试信息：开始初始化
    std::wstring debugMsg = L"CategoryManager: 开始初始化，原始配置文件路径: " + m_configPath + L"\n";
    OutputDebugStringW(debugMsg.c_str());
    
    // 尝试将路径转换为绝对路径
    std::wstring resolvedPath = normalizePath(m_configPath);
    debugMsg = L"CategoryManager: 解析后的配置文件路径: " + resolvedPath + L"\n";
    OutputDebugStringW(debugMsg.c_str());
    
    // 更新为解析后的路径
    if (!resolvedPath.empty()) {
        m_configPath = resolvedPath;
    }
    
    // 确保配置目录存在
    bool dirResult = ensureConfigDirectory();
    debugMsg = L"CategoryManager: ensureConfigDirectory 返回结果: " + std::to_wstring(dirResult) + L"\n";
    OutputDebugStringW(debugMsg.c_str());
    
    // 加载配置，如果失败则创建默认分类
    OutputDebugStringW(L"CategoryManager: 开始加载配置文件\n");
    if (!loadConfig()) {
        OutputDebugStringW(L"CategoryManager: 配置加载失败，创建默认分类\n");
        createDefaultCategories();
        debugMsg = L"CategoryManager: 默认分类创建完成，分类数量: " + std::to_wstring(m_categories.size()) + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        if (saveConfig()) {
            OutputDebugStringW(L"CategoryManager: 默认分类保存成功\n");
        } else {
            OutputDebugStringW(L"CategoryManager: 默认分类保存失败\n");
        }
    } else {
        OutputDebugStringW(L"CategoryManager: 配置加载成功\n");
        debugMsg = L"CategoryManager: 配置加载成功，分类数量: " + std::to_wstring(m_categories.size()) + L"\n";
        OutputDebugStringW(debugMsg.c_str());
    }
    
    // 调试信息：显示加载的分类数量
    debugMsg = L"CategoryManager: 初始化完成，分类数量: " + std::to_wstring(m_categories.size()) + L"\n";
    OutputDebugStringW(debugMsg.c_str());
    
    // 输出所有分类信息用于调试
    for (const auto& category : m_categories) {
        debugMsg = L"CategoryManager: 分类信息 - ID: " + category.id + L", 名称: " + category.name + L", 描述: " + category.description + L", 顺序: " + std::to_wstring(category.order) + L"\n";
        OutputDebugStringW(debugMsg.c_str());
    }
}

/**
 * @brief 加载分类配置
 * @return bool 加载是否成功
 */
bool CategoryManager::loadConfig() {
    try {
        // 将相对路径转换为绝对路径
        std::wstring fullPath = m_configPath;
        
        // 调试信息：显示原始路径
        std::wstring debugMsg = L"CategoryManager: loadConfig 开始，原始路径: " + m_configPath + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 检查文件是否存在
        DWORD fileAttributes = GetFileAttributesW(m_configPath.c_str());
        if (fileAttributes == INVALID_FILE_ATTRIBUTES) {
            DWORD error = GetLastError();
            debugMsg = L"CategoryManager: 文件不存在或无法访问，错误码: " + std::to_wstring(error) + L"\n";
            OutputDebugStringW(debugMsg.c_str());
            
            // 尝试使用exe路径构建完整路径
            wchar_t exePath[MAX_PATH];
            if (GetModuleFileNameW(NULL, exePath, MAX_PATH)) {
                // 获取exe所在目录
                PathRemoveFileSpecW(exePath);
                
                std::wstring fullConfigPath = std::wstring(exePath) + L"\\" + m_configPath;
                debugMsg = L"CategoryManager: 尝试exe路径: " + fullConfigPath + L"\n";
                OutputDebugStringW(debugMsg.c_str());
                
                fileAttributes = GetFileAttributesW(fullConfigPath.c_str());
                if (fileAttributes != INVALID_FILE_ATTRIBUTES) {
                    fullPath = fullConfigPath;
                    debugMsg = L"CategoryManager: exe路径有效\n";
                    OutputDebugStringW(debugMsg.c_str());
                } else {
                    error = GetLastError();
                    debugMsg = L"CategoryManager: exe路径也不存在，错误码: " + std::to_wstring(error) + L"\n";
                    OutputDebugStringW(debugMsg.c_str());
                }
            }
        } else {
            debugMsg = L"CategoryManager: 原始路径有效\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        // 尝试打开文件
        std::ifstream file(fullPath, std::ios::in);
        if (!file.is_open()) {
            debugMsg = L"CategoryManager: 无法打开文件: " + fullPath + L"\n";
            OutputDebugStringW(debugMsg.c_str());
            
            // 尝试不同的打开模式
            file.open(fullPath, std::ios::in | std::ios::binary);
            if (!file.is_open()) {
                debugMsg = L"CategoryManager: 无法以二进制模式打开文件: " + fullPath + L"\n";
                OutputDebugStringW(debugMsg.c_str());
                return false;
            } else {
                debugMsg = L"CategoryManager: 以二进制模式成功打开文件: " + fullPath + L"\n";
                OutputDebugStringW(debugMsg.c_str());
            }
        } else {
            debugMsg = L"CategoryManager: 成功打开文件: " + fullPath + L"\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        // 检查文件是否为空
        file.seekg(0, std::ios::end);
        std::streampos fileSize = file.tellg();
        file.seekg(0, std::ios::beg); // 重置文件指针
        
        debugMsg = L"CategoryManager: 文件大小: " + std::to_wstring(fileSize) + L" 字节\n";
        OutputDebugStringW(debugMsg.c_str());
        
        if (fileSize == 0) {
            file.close();
            debugMsg = L"CategoryManager: 文件为空\n";
            OutputDebugStringW(debugMsg.c_str());
            return false; // 文件为空，加载失败
        }
        
        // 读取文件内容到字符串
        std::string fileContent((std::istreambuf_iterator<char>(file)),
                               std::istreambuf_iterator<char>());
        file.close();
        
        debugMsg = L"CategoryManager: 读取到文件内容长度: " + std::to_wstring(fileContent.length()) + L" 字符\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 检查是否包含BOM标记并移除
        if (fileContent.length() >= 3 && 
            static_cast<unsigned char>(fileContent[0]) == 0xEF &&
            static_cast<unsigned char>(fileContent[1]) == 0xBB &&
            static_cast<unsigned char>(fileContent[2]) == 0xBF) {
            fileContent = fileContent.substr(3); // 移除BOM
            debugMsg = L"CategoryManager: 移除了UTF-8 BOM标记\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        // 输出文件内容的前200个字符用于调试
        if (!fileContent.empty()) {
            std::string preview = fileContent.substr(0, (std::min)(size_t(200), fileContent.length()));
            debugMsg = L"CategoryManager: 文件内容预览: " + std::wstring(preview.begin(), preview.end()) + L"\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        // 解析JSON
        json config = json::parse(fileContent);
        
        // 调试信息：显示JSON解析结果
        debugMsg = L"CategoryManager: JSON解析成功\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 检查JSON结构
        if (config.is_object()) {
            debugMsg = L"CategoryManager: JSON是对象类型\n";
            OutputDebugStringW(debugMsg.c_str());
            
            if (config.contains("categories")) {
                debugMsg = L"CategoryManager: JSON包含categories键\n";
                OutputDebugStringW(debugMsg.c_str());
                
                auto categories = config["categories"];
                if (categories.is_array()) {
                    debugMsg = L"CategoryManager: categories是数组类型，大小: " + std::to_wstring(categories.size()) + L"\n";
                    OutputDebugStringW(debugMsg.c_str());
                } else {
                    debugMsg = L"CategoryManager: categories不是数组类型\n";
                    OutputDebugStringW(debugMsg.c_str());
                }
            } else {
                debugMsg = L"CategoryManager: JSON不包含categories键\n";
                OutputDebugStringW(debugMsg.c_str());
                
                // 输出所有键名用于调试
                for (auto it = config.begin(); it != config.end(); ++it) {
                    std::string key = it.key();
                    debugMsg = L"CategoryManager: JSON键名: " + std::wstring(key.begin(), key.end()) + L"\n";
                    OutputDebugStringW(debugMsg.c_str());
                }
            }
        } else {
            debugMsg = L"CategoryManager: JSON不是对象类型\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        // 清空现有数据
        m_categories.clear();
        m_fileMappings.clear();
        
        // 加载分类
        if (config.contains("categories")) {
            debugMsg = L"CategoryManager: JSON包含categories键\n";
            OutputDebugStringW(debugMsg.c_str());
            
            for (const auto& catJson : config["categories"]) {
                FileCategory category;
                category.fromJson(catJson);
                m_categories.push_back(category);
                debugMsg = L"CategoryManager: 加载分类: " + category.name + L" (ID: " + category.id + L")\n";
                OutputDebugStringW(debugMsg.c_str());
            }
        } else {
            debugMsg = L"CategoryManager: JSON不包含categories键\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        // 加载文件映射
        if (config.contains("fileMappings")) {
            for (const auto& mappingJson : config["fileMappings"]) {
                FileCategoryMapping mapping;
                mapping.fromJson(mappingJson);
                m_fileMappings.push_back(mapping);
            }
        }
        
        debugMsg = L"CategoryManager: loadConfig 完成，分类数量: " + std::to_wstring(m_categories.size()) + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        return true;
    }
    catch (const json::exception& e) {
        // JSON解析异常
        std::string errorMsg = "CategoryManager: JSON解析异常: " + std::string(e.what()) + "\n";
        OutputDebugStringA(errorMsg.c_str());
        return false;
    }
    catch (const std::exception& e) {
        // 其他异常
        std::string errorMsg = "CategoryManager: 异常: " + std::string(e.what()) + "\n";
        OutputDebugStringA(errorMsg.c_str());
        return false;
    }
    catch (...) {
        // 未知异常
        OutputDebugStringA("CategoryManager: 未知异常\n");
        return false;
    }
}

/**
 * @brief 保存分类配置
 */
bool CategoryManager::saveConfig() {
    try {
        // 确保配置目录存在
        if (!ensureConfigDirectory()) {
            // 调试信息：目录创建失败
            OutputDebugStringW(L"CategoryManager: 配置目录创建失败\n");
            return false;
        }
        
        json config;
        
        // 保存分类
        json categoriesArray = json::array();
        for (const auto& category : m_categories) {
            categoriesArray.push_back(category.toJson());
        }
        config["categories"] = categoriesArray;
        
        // 保存文件映射
        json mappingsArray = json::array();
        for (const auto& mapping : m_fileMappings) {
            mappingsArray.push_back(mapping.toJson());
        }
        config["fileMappings"] = mappingsArray;
        
        // 生成JSON字符串
        std::string jsonString = config.dump(4); // 缩进4个空格，便于阅读
        
        // 以二进制模式打开文件，写入UTF-8 BOM
        std::ofstream file(m_configPath, std::ios::binary | std::ios::trunc);
        if (!file.is_open()) {
            // 调试信息：文件打开失败
            std::wstring debugMsg = L"CategoryManager: 无法打开配置文件: " + m_configPath + L"\n";
            OutputDebugStringW(debugMsg.c_str());
            return false;
        }
        
        // 写入UTF-8 BOM标记
        const unsigned char bom[] = {0xEF, 0xBB, 0xBF};
        file.write(reinterpret_cast<const char*>(bom), 3);
        
        // 写入JSON内容
        file << jsonString;
        file.close(); // 确保文件正确关闭
        
        // 调试信息：保存成功
        OutputDebugStringW(L"CategoryManager: 配置文件保存成功\n");
        return true;
    }
    catch (const std::exception&) {
        // 调试信息：异常信息
        OutputDebugStringA("CategoryManager: 保存配置时发生异常\n");
        return false;
    }
}

/**
 * @brief 添加新分类
 */
bool CategoryManager::addCategory(const FileCategory& category) {
    // 检查是否已存在同名分类
    for (const auto& existingCat : m_categories) {
        if (existingCat.name == category.name) {
            return false; // 分类已存在
        }
    }
    
    m_categories.push_back(category);
    return saveConfig();
}

/**
 * @brief 删除分类
 */
bool CategoryManager::removeCategory(const std::wstring& categoryId) {
    // 移除分类
    auto it = std::remove_if(m_categories.begin(), m_categories.end(),
        [&categoryId](const FileCategory& cat) {
            return cat.id == categoryId;
        });
    
    if (it != m_categories.end()) {
        m_categories.erase(it, m_categories.end());
        
        // 移除相关的文件映射
        m_fileMappings.erase(
            std::remove_if(m_fileMappings.begin(), m_fileMappings.end(),
                [&categoryId](const FileCategoryMapping& mapping) {
                    return mapping.categoryId == categoryId;
                }),
            m_fileMappings.end()
        );
        
        return saveConfig();
    }
    
    return false;
}

/**
 * @brief 更新分类信息
 */
bool CategoryManager::updateCategory(const FileCategory& category) {
    for (auto& existingCat : m_categories) {
        if (existingCat.id == category.id) {
            existingCat = category;
            return saveConfig();
        }
    }
    return false;
}

/**
 * @brief 根据ID获取分类
 */
FileCategory* CategoryManager::getCategoryById(const std::wstring& categoryId) {
    for (auto& category : m_categories) {
        if (category.id == categoryId) {
            return &category;
        }
    }
    return nullptr;
}

/**
 * @brief 根据名称获取分类
 */
FileCategory* CategoryManager::getCategoryByName(const std::wstring& name) {
    for (auto& category : m_categories) {
        if (category.name == name) {
            return &category;
        }
    }
    return nullptr;
}

/**
 * @brief 重命名分类
 */
bool CategoryManager::renameCategory(const std::wstring& oldName, const std::wstring& newName) {
    if (oldName == newName) {
        return true; // 名称相同，无需重命名
    }
    
    // 检查新名称是否已存在
    if (getCategoryByName(newName)) {
        return false; // 新名称已存在
    }
    
    // 查找并重命名分类
    for (auto& category : m_categories) {
        if (category.name == oldName) {
            category.name = newName;
            return saveConfig();
        }
    }
    
    return false; // 原分类不存在
}

/**
 * @brief 重命名分类（根据ID）
 */
bool CategoryManager::renameCategoryById(const std::wstring& categoryId, const std::wstring& newName) {
    // 首先根据新名称查找是否已存在
    if (getCategoryByName(newName)) {
        return false; // 新名称已存在
    }
    
    // 查找并重命名分类
    for (auto& category : m_categories) {
        if (category.id == categoryId) {
            category.name = newName;
            return saveConfig();
        }
    }
    
    return false; // 原分类不存在
}

/**
 * @brief 设置文件的分类
 */
bool CategoryManager::setFileCategory(const std::wstring& filePath, const std::wstring& categoryId) {
    std::wstring normalizedPath = normalizePath(filePath);
    
    // 检查分类是否存在
    if (!getCategoryById(categoryId)) {
        return false;
    }
    
    // 移除现有的映射
    removeFileCategory(normalizedPath);
    
    // 添加新的映射
    m_fileMappings.push_back(FileCategoryMapping(normalizedPath, categoryId));
    return saveConfig();
}

/**
 * @brief 获取文件的分类
 */
std::wstring CategoryManager::getFileCategory(const std::wstring& filePath) const {
    std::wstring normalizedPath = normalizePath(filePath);
    
    for (const auto& mapping : m_fileMappings) {
        if (mapping.filePath == normalizedPath) {
            return mapping.categoryId;
        }
    }
    
    return getDefaultCategoryId(); // 返回默认分类
}

/**
 * @brief 移除文件的分类
 */
bool CategoryManager::removeFileCategory(const std::wstring& filePath) {
    std::wstring normalizedPath = normalizePath(filePath);
    
    auto it = std::remove_if(m_fileMappings.begin(), m_fileMappings.end(),
        [&normalizedPath](const FileCategoryMapping& mapping) {
            return mapping.filePath == normalizedPath;
        });
    
    if (it != m_fileMappings.end()) {
        m_fileMappings.erase(it, m_fileMappings.end());
        return saveConfig();
    }
    
    return false;
}

/**
 * @brief 获取指定分类下的所有文件路径
 */
std::vector<std::wstring> CategoryManager::getFilesByCategory(const std::wstring& categoryId) const {
    std::vector<std::wstring> files;
    
    for (const auto& mapping : m_fileMappings) {
        if (mapping.categoryId == categoryId) {
            files.push_back(mapping.filePath);
        }
    }
    
    return files;
}

/**
 * @brief 添加文件到分类（根据分类名称）
 */
bool CategoryManager::addFileToCategory(const std::wstring& filePath, const std::wstring& categoryName) {
    // 根据分类名称查找分类ID
    FileCategory* category = getCategoryByName(categoryName);
    if (!category) {
        return false; // 分类不存在
    }
    
    // 使用现有的setFileCategory方法
    return setFileCategory(filePath, category->id);
}

/**
 * @brief 从分类中移除文件（根据分类名称）
 */
bool CategoryManager::removeFileFromCategory(const std::wstring& filePath) {
    // 使用现有的removeFileCategory方法
    return removeFileCategory(filePath);
}

/**
 * @brief 创建默认分类
 */
void CategoryManager::createDefaultCategories() {
    m_categories.clear();
    
    // 创建默认分类，使用固定的分类ID
    FileCategory defaultCategory(L"全部", L"未分类的文件", 0);
    defaultCategory.id = getDefaultCategoryId();
    m_categories.push_back(defaultCategory);
    
    FileCategory programmingCategory(L"编程", L"编程相关的文件", 1);
    programmingCategory.id = L"programming";
    m_categories.push_back(programmingCategory);
    
    FileCategory workCategory(L"工作", L"工作相关的文件", 2);
    workCategory.id = L"work";
    m_categories.push_back(workCategory);
    
    FileCategory lifeCategory(L"生活", L"生活相关的文件", 3);
    lifeCategory.id = L"life";
    m_categories.push_back(lifeCategory);
    
    FileCategory studyCategory(L"学习", L"学习相关的文件", 4);
    studyCategory.id = L"study";
    m_categories.push_back(studyCategory);
}

/**
 * @brief 确保配置文件目录存在
 */
bool CategoryManager::ensureConfigDirectory() const {
    try {
        // 调试信息：显示原始配置路径
        std::wstring debugMsg = L"CategoryManager: 原始配置路径: " + m_configPath + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 从路径中提取目录
        size_t lastBackslash = m_configPath.find_last_of(L'\\');
        size_t lastForwardSlash = m_configPath.find_last_of(L'/');
        size_t lastSeparator = std::max(lastBackslash, lastForwardSlash);
        
        if (lastSeparator != std::wstring::npos) {
            std::wstring directory = m_configPath.substr(0, lastSeparator);
            
            debugMsg = L"CategoryManager: 需要创建的目录: " + directory + L"\n";
            OutputDebugStringW(debugMsg.c_str());
            
            // 尝试创建目录
            if (CreateDirectoryW(directory.c_str(), NULL) || GetLastError() == ERROR_ALREADY_EXISTS) {
                debugMsg = L"CategoryManager: 目录已存在或创建成功: " + directory + L"\n";
                OutputDebugStringW(debugMsg.c_str());
            } else {
                DWORD error = GetLastError();
                debugMsg = L"CategoryManager: 创建目录失败，错误码: " + std::to_wstring(error) + L"\n";
                OutputDebugStringW(debugMsg.c_str());
            }
        } else {
            debugMsg = L"CategoryManager: 无法从路径中提取目录: " + m_configPath + L"\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        // 检查文件是否存在
        DWORD fileAttributes = GetFileAttributesW(m_configPath.c_str());
        if (fileAttributes == INVALID_FILE_ATTRIBUTES) {
            debugMsg = L"CategoryManager: 配置文件不存在: " + m_configPath + L"\n";
            OutputDebugStringW(debugMsg.c_str());
        } else {
            debugMsg = L"CategoryManager: 配置文件存在: " + m_configPath + L"\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        return true;
    }
    catch (const std::exception& e) {
        std::string errorMsg = "CategoryManager: ensureConfigDirectory异常: " + std::string(e.what()) + "\n";
        OutputDebugStringA(errorMsg.c_str());
        return false;
    }
}

/**
 * @brief 从文件路径生成标准化的路径
 * 修复版本：使用exe路径而不是当前工作目录来解析相对路径
 */
std::wstring CategoryManager::normalizePath(const std::wstring& path) const {
    if (path.empty()) {
        return path;
    }
    
    // 调试信息：显示原始输入路径
    std::wstring debugMsg = L"CategoryManager::normalizePath - 输入: '" + path + L"'\n";
    OutputDebugStringW(debugMsg.c_str());
    
    // 检查是否是绝对路径
    if (path.find(L':') != std::wstring::npos) {
        // 绝对路径，直接返回
        debugMsg = L"CategoryManager::normalizePath - 检测为绝对路径，返回: '" + path + L"'\n";
        OutputDebugStringW(debugMsg.c_str());
        return path;
    }
    
    // 相对路径，需要相对于exe路径转换为绝对路径
    wchar_t exePath[MAX_PATH];
    if (GetModuleFileNameW(NULL, exePath, MAX_PATH) > 0) {
        debugMsg = L"CategoryManager::normalizePath - exe路径: '" + std::wstring(exePath) + L"'\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 获取exe所在目录
        wchar_t exeDir[MAX_PATH];
        wcscpy_s(exeDir, MAX_PATH, exePath);
        if (PathRemoveFileSpecW(exeDir)) {
            debugMsg = L"CategoryManager::normalizePath - exe目录: '" + std::wstring(exeDir) + L"'\n";
            OutputDebugStringW(debugMsg.c_str());
            
            // 使用PathCombine相对于exe目录解析相对路径
            wchar_t combinedPath[MAX_PATH];
            if (PathCombineW(combinedPath, exeDir, path.c_str())) {
                debugMsg = L"CategoryManager::normalizePath - 组合路径: '" + std::wstring(combinedPath) + L"'\n";
                OutputDebugStringW(debugMsg.c_str());
                
                // 使用PathCanonicalize规范化路径（处理..和.符号）
                wchar_t canonicalPath[MAX_PATH];
                if (PathCanonicalizeW(canonicalPath, combinedPath)) {
                    std::wstring result = canonicalPath;
                    debugMsg = L"CategoryManager::normalizePath - 规范化后路径: '" + result + L"'\n";
                    OutputDebugStringW(debugMsg.c_str());
                    return result;
                } else {
                    // PathCanonicalize失败，使用PathCombine的结果
                    std::wstring result = combinedPath;
                    debugMsg = L"CategoryManager::normalizePath - PathCanonicalize失败，使用组合路径: '" + result + L"'\n";
                    OutputDebugStringW(debugMsg.c_str());
                    return result;
                }
            } else {
                // PathCombine失败，尝试简单方案
                debugMsg = L"CategoryManager::normalizePath - PathCombine失败\n";
                OutputDebugStringW(debugMsg.c_str());
                
                std::wstring normalized = path;
                // 标准化路径分隔符
                for (auto& ch : normalized) {
                    if (ch == L'/') {
                        ch = L'\\';
                    }
                }
                
                std::wstring dirStr = exeDir;
                if (!dirStr.empty() && dirStr.back() == L'\\') {
                    dirStr.pop_back();
                }
                
                std::wstring result = dirStr + L"\\" + normalized;
                debugMsg = L"CategoryManager::normalizePath - 使用简单拼接: '" + result + L"'\n";
                OutputDebugStringW(debugMsg.c_str());
                return result;
            }
        } else {
            // 获取exe目录失败
            debugMsg = L"CategoryManager::normalizePath - 获取exe目录失败\n";
            OutputDebugStringW(debugMsg.c_str());
        }
    } else {
        // 获取exe路径失败
        debugMsg = L"CategoryManager::normalizePath - 获取exe路径失败\n";
        OutputDebugStringW(debugMsg.c_str());
    }
    
    // 所有方法都失败，返回原始路径
    debugMsg = L"CategoryManager::normalizePath - 返回原始路径: '" + path + L"'\n";
    OutputDebugStringW(debugMsg.c_str());
    return path;
}