// Category Manager Header File
// 负责管理文件分类（Programming, Work, Life, etc.）

#pragma once

#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <windows.h>
#include "../../json/json.hpp"

using json = nlohmann::json;

/**
 * @brief File Category Information Structure
 */
struct FileCategory {
    std::wstring id;           // Category ID
    std::wstring name;         // Category Name
    std::wstring description;  // Category Description
    int order;                 // Display Order
    
    FileCategory() : order(0) {}
    FileCategory(const std::wstring& name, const std::wstring& desc = L"", int order = 0)
        : name(name), description(desc), order(order) {
        // Generate Unique ID
        id = L"cat_" + std::to_wstring(std::hash<std::wstring>{}(name + desc));
    }
    
    // Convert to JSON
    json toJson() const {
        // Convert wide string using UTF-8 encoding
        auto toUtf8 = [](const std::wstring& wstr) -> std::string {
            if (wstr.empty()) return "";
            int size_needed = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), NULL, 0, NULL, NULL);
            std::string str(size_needed, 0);
            WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), &str[0], size_needed, NULL, NULL);
            return str;
        };
        
        return {
            {"id", toUtf8(id)},
            {"name", toUtf8(name)},
            {"description", toUtf8(description)},
            {"order", order}
        };
    }
    
    // Load from JSON
    void fromJson(const json& j) {
        // Convert to wide string using UTF-8 encoding
        auto toWide = [](const std::string& str) -> std::wstring {
            if (str.empty()) return L"";
            int size_needed = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), NULL, 0);
            std::wstring wstr(size_needed, 0);
            MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), &wstr[0], size_needed);
            return wstr;
        };
        
        if (j.contains("id")) {
            std::string idStr = j["id"];
            id = toWide(idStr);
        }
        if (j.contains("name")) {
            std::string nameStr = j["name"];
            name = toWide(nameStr);
        }
        if (j.contains("description")) {
            std::string descStr = j["description"];
            description = toWide(descStr);
        }
        if (j.contains("order")) {
            order = j["order"];
        }
    }
};

/**
 * @brief File and Category Association Information
 */
struct FileCategoryMapping {
    std::wstring filePath;     // File Path
    std::wstring categoryId;   // Category ID
    
    FileCategoryMapping() = default;
    FileCategoryMapping(const std::wstring& path, const std::wstring& catId)
        : filePath(path), categoryId(catId) {}
    
    // Convert to JSON
    json toJson() const {
        // Convert wide string using UTF-8 encoding
        auto toUtf8 = [](const std::wstring& wstr) -> std::string {
            if (wstr.empty()) return "";
            int size_needed = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), NULL, 0, NULL, NULL);
            std::string str(size_needed, 0);
            WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), &str[0], size_needed, NULL, NULL);
            return str;
        };
        
        return {
            {"filePath", toUtf8(filePath)},
            {"categoryId", toUtf8(categoryId)}
        };
    }
    
    // Load from JSON
    void fromJson(const json& j) {
        // Convert to wide string using UTF-8 encoding
        auto toWide = [](const std::string& str) -> std::wstring {
            if (str.empty()) return L"";
            int size_needed = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), NULL, 0);
            std::wstring wstr(size_needed, 0);
            MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), &wstr[0], size_needed);
            return wstr;
        };
        
        if (j.contains("filePath")) {
            std::string pathStr = j["filePath"];
            filePath = toWide(pathStr);
        }
        if (j.contains("categoryId")) {
            std::string catIdStr = j["categoryId"];
            categoryId = toWide(catIdStr);
        }
    }
};

/**
 * @brief Category Manager Class
 */
class CategoryManager {
private:
    std::vector<FileCategory> m_categories;           // Category List
    std::vector<FileCategoryMapping> m_fileMappings;   // File and Category Mapping
    std::wstring m_configPath;                         // Configuration Files路径
    std::wstring m_fileMappingsPath;                    // File Mapping Save Path Separately
    
public:
    CategoryManager();
    ~CategoryManager() = default;
    
    /**
     * @brief Initialize Category Manager
     * @param configPath Configuration Files路径
     */
    void initialize(const std::wstring& configPath);
    
    /**
     * @brief Load Category Configuration
     */
    bool loadConfig();
    
    /**
     * @brief Save Category Configuration
     */
    bool saveConfig();
    
    /**
     * @brief Get All Categories
     */
    const std::vector<FileCategory>& getCategories() const { return m_categories; }
    
    /**
     * @brief Add New Category
     * @param category 分类信息
     */
    bool addCategory(const FileCategory& category);
    
    /**
     * @brief Delete Category
     * @param categoryId Category ID
     */
    bool removeCategory(const std::wstring& categoryId);
    
    /**
     * @brief Update Category Information
     * @param category 分类信息
     */
    bool updateCategory(const FileCategory& category);
    
    /**
     * @brief Get Category by ID
     * @param categoryId Category ID
     */
    FileCategory* getCategoryById(const std::wstring& categoryId);
    
    /**
     * @brief Get Category by Name
     * @param name Category Name
     */
    FileCategory* getCategoryByName(const std::wstring& name);
    
    /**
     * @brief Rename Category
     * @param oldName 原名称
     * @param newName 新名称
     */
    bool renameCategory(const std::wstring& oldName, const std::wstring& newName);
    
    /**
     * @brief Rename Category（根据ID）
     * @param categoryId Category ID
     * @param newName 新名称
     */
    bool renameCategoryById(const std::wstring& categoryId, const std::wstring& newName);
    
    /**
     * @brief Set File Category
     * @param filePath File Path
     * @param categoryId Category ID
     */
    bool setFileCategory(const std::wstring& filePath, const std::wstring& categoryId);
    
    /**
     * @brief Get File Category
     * @param filePath File Path
     */
    std::wstring getFileCategory(const std::wstring& filePath) const;
    
    /**
     * @brief Remove File Category
     * @param filePath File Path
     */
    bool removeFileCategory(const std::wstring& filePath);
    
    /**
     * @brief 添加文件到分类（根据Category Name）
     * @param filePath File Path
     * @param categoryName Category Name
     */
    bool addFileToCategory(const std::wstring& filePath, const std::wstring& categoryName);
    
    /**
     * @brief 从分类中移除文件（根据Category Name）
     * @param filePath File Path
     */
    bool removeFileFromCategory(const std::wstring& filePath);
    
    /**
     * @brief 获取指定分类下的所有File Path
     * @param categoryId Category ID
     */
    std::vector<std::wstring> getFilesByCategory(const std::wstring& categoryId) const;
    
    /**
     * @brief 创建Default Category
     */
    void createDefaultCategories();
    
    /**
     * @brief 获取Default CategoryID
     */
    static std::wstring getDefaultCategoryId() { return L"default"; }
    
    /**
     * @brief 获取Default Category名称
     */
    static std::wstring getDefaultCategoryName() { return L"All"; }
    
    /**
     * @brief Save File Mapping to Separate JSON File
     */
    bool saveFileMappings();
    
    /**
     * @brief Load File Mapping from Separate JSON File
     */
    bool loadFileMappings();
    
private:
    /**
     * @brief 确保Configuration Files目录存在
     */
    bool ensureConfigDirectory() const;
    
    /**
     * @brief 从File Path生成标准化的路径
     */
    std::wstring normalizePath(const std::wstring& path) const;
};