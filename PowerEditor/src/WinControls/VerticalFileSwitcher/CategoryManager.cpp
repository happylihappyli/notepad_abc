// 分类管理器实现文件

#include "CategoryManager.h"
#include <fstream>
#include <algorithm>
#include <filesystem>
#include <windows.h>
#include "Parameters.h"

namespace fs = std::filesystem;

CategoryManager::CategoryManager() {
    // 默认配置文件路径
    m_configPath = L"categories.json";
}

/**
 * @brief 初始化分类管理器
 */
void CategoryManager::initialize(const std::wstring& configPath) {
    if (!configPath.empty()) {
        m_configPath = configPath;
    }
    
    // 调试信息：开始初始化
    std::wstring debugMsg = L"CategoryManager: 开始初始化，配置文件路径: " + m_configPath + L"\n";
    OutputDebugStringW(debugMsg.c_str());
    
    // 确保配置目录存在
    bool dirResult = ensureConfigDirectory();
    debugMsg = L"CategoryManager: ensureConfigDirectory 返回结果: " + std::to_wstring(dirResult) + L"\n";
    OutputDebugStringW(debugMsg.c_str());
    
    // 加载配置，如果失败则创建默认分类
    if (!loadConfig()) {
        OutputDebugStringW(L"CategoryManager: 配置加载失败，创建默认分类\n");
        createDefaultCategories();
        if (saveConfig()) {
            OutputDebugStringW(L"CategoryManager: 默认分类保存成功\n");
        } else {
            OutputDebugStringW(L"CategoryManager: 默认分类保存失败\n");
        }
    } else {
        OutputDebugStringW(L"CategoryManager: 配置加载成功\n");
    }
}

/**
 * @brief 加载分类配置
 */
bool CategoryManager::loadConfig() {
    try {
        // 将相对路径转换为绝对路径
        fs::path configPath(m_configPath);
        if (configPath.is_relative()) {
            configPath = fs::absolute(configPath);
        }
        
        std::ifstream file(configPath);
        if (!file.is_open()) {
            return false;
        }
        
        // 检查文件是否为空
        file.seekg(0, std::ios::end);
        if (file.tellg() == 0) {
            file.close();
            return false; // 文件为空，加载失败
        }
        file.seekg(0, std::ios::beg); // 重置文件指针
        
        json config;
        file >> config;
        
        // 清空现有数据
        m_categories.clear();
        m_fileMappings.clear();
        
        // 加载分类
        if (config.contains("categories")) {
            for (const auto& catJson : config["categories"]) {
                FileCategory category;
                category.fromJson(catJson);
                m_categories.push_back(category);
            }
        }
        
        // 加载文件映射
        if (config.contains("fileMappings")) {
            for (const auto& mappingJson : config["fileMappings"]) {
                FileCategoryMapping mapping;
                mapping.fromJson(mappingJson);
                m_fileMappings.push_back(mapping);
            }
        }
        
        return true;
    }
    catch (const std::exception&) {
        // 加载失败，返回false
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
        
        // 将相对路径转换为绝对路径
        fs::path configPath(m_configPath);
        if (configPath.is_relative()) {
            // 使用当前工作目录作为基础路径
            fs::path currentDir = fs::current_path();
            configPath = currentDir / configPath;
        }
        
        // 调试信息：显示最终配置路径
        std::wstring debugMsg = L"CategoryManager: 最终配置路径: " + configPath.wstring() + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 生成JSON字符串
        std::string jsonString = config.dump(4); // 缩进4个空格，便于阅读
        
        // 以二进制模式打开文件，写入UTF-8 BOM
        std::ofstream file(configPath, std::ios::binary | std::ios::trunc);
        if (!file.is_open()) {
            // 调试信息：文件打开失败
            debugMsg = L"CategoryManager: 无法打开配置文件: " + configPath.wstring() + L"\n";
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
        fs::path configPath(m_configPath);
        
        // 调试信息：显示原始配置路径
        std::wstring debugMsg = L"CategoryManager: 原始配置路径: " + m_configPath + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 将相对路径转换为绝对路径
        if (configPath.is_relative()) {
            // 使用当前工作目录作为基础路径
            fs::path currentDir = fs::current_path();
            configPath = currentDir / configPath;
            debugMsg = L"CategoryManager: 转换为绝对路径: " + configPath.wstring() + L"\n";
            OutputDebugStringW(debugMsg.c_str());
        }
        
        fs::path configDir = configPath.parent_path();
        
        // 调试信息：显示配置路径和目录信息
        debugMsg = L"CategoryManager: 配置路径: " + configPath.wstring() + L", 配置目录: " + configDir.wstring() + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 检查配置目录是否为空（配置文件在当前目录）
        if (configDir.empty()) {
            OutputDebugStringW(L"CategoryManager: 配置文件在当前目录，不需要创建目录\n");
            return true;
        }
        
        // 检查目录是否等于当前工作目录
        fs::path currentDir = fs::current_path();
        debugMsg = L"CategoryManager: 当前工作目录: " + currentDir.wstring() + L"\n";
        OutputDebugStringW(debugMsg.c_str());
        
        // 如果目录不存在，则创建目录
        if (!fs::exists(configDir)) {
            OutputDebugStringW(L"CategoryManager: 配置目录不存在，正在创建目录\n");
            bool result = fs::create_directories(configDir);
            if (result) {
                OutputDebugStringW(L"CategoryManager: 配置目录创建成功\n");
            } else {
                OutputDebugStringW(L"CategoryManager: 配置目录创建失败\n");
            }
            return result;
        }
        
        OutputDebugStringW(L"CategoryManager: 配置目录已存在\n");
        return true;
    }
    catch (const std::exception&) {
        std::string errorMsg = "CategoryManager: ensureConfigDirectory异常\n";
        OutputDebugStringA(errorMsg.c_str());
        return false;
    }
}

/**
 * @brief 从文件路径生成标准化的路径
 */
std::wstring CategoryManager::normalizePath(const std::wstring& path) const {
    try {
        fs::path normalized(path);
        normalized = fs::absolute(normalized);
        normalized = normalized.lexically_normal();
        return normalized.wstring();
    }
    catch (const std::exception&) {
        return path; // 如果标准化失败，返回原路径
    }
}