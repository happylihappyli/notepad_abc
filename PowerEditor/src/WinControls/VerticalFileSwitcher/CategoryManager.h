// 分类管理器头文件
// 负责管理文件分类（编程、工作、生活等）

#pragma once

#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <windows.h>
#include "json.hpp"

using json = nlohmann::json;

/**
 * @brief 文件分类信息结构体
 */
struct FileCategory {
    std::wstring id;           // 分类ID
    std::wstring name;         // 分类名称
    std::wstring description;  // 分类描述
    int order;                 // 显示顺序
    
    FileCategory() : order(0) {}
    FileCategory(const std::wstring& name, const std::wstring& desc = L"", int order = 0)
        : name(name), description(desc), order(order) {
        // 生成唯一ID
        id = L"cat_" + std::to_wstring(std::hash<std::wstring>{}(name + desc));
    }
    
    // 转换为JSON
    json toJson() const {
        // 使用UTF-8编码转换宽字符串
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
    
    // 从JSON加载
    void fromJson(const json& j) {
        // 使用UTF-8编码转换到宽字符串
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
 * @brief 文件与分类的关联信息
 */
struct FileCategoryMapping {
    std::wstring filePath;     // 文件路径
    std::wstring categoryId;   // 分类ID
    
    FileCategoryMapping() = default;
    FileCategoryMapping(const std::wstring& path, const std::wstring& catId)
        : filePath(path), categoryId(catId) {}
    
    // 转换为JSON
    json toJson() const {
        // 使用UTF-8编码转换宽字符串
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
    
    // 从JSON加载
    void fromJson(const json& j) {
        // 使用UTF-8编码转换到宽字符串
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
 * @brief 分类管理器类
 */
class CategoryManager {
private:
    std::vector<FileCategory> m_categories;           // 分类列表
    std::vector<FileCategoryMapping> m_fileMappings;   // 文件与分类的映射
    std::wstring m_configPath;                         // 配置文件路径
    
public:
    CategoryManager();
    ~CategoryManager() = default;
    
    /**
     * @brief 初始化分类管理器
     * @param configPath 配置文件路径
     */
    void initialize(const std::wstring& configPath);
    
    /**
     * @brief 加载分类配置
     */
    bool loadConfig();
    
    /**
     * @brief 保存分类配置
     */
    bool saveConfig();
    
    /**
     * @brief 获取所有分类
     */
    const std::vector<FileCategory>& getCategories() const { return m_categories; }
    
    /**
     * @brief 添加新分类
     * @param category 分类信息
     */
    bool addCategory(const FileCategory& category);
    
    /**
     * @brief 删除分类
     * @param categoryId 分类ID
     */
    bool removeCategory(const std::wstring& categoryId);
    
    /**
     * @brief 更新分类信息
     * @param category 分类信息
     */
    bool updateCategory(const FileCategory& category);
    
    /**
     * @brief 根据ID获取分类
     * @param categoryId 分类ID
     */
    FileCategory* getCategoryById(const std::wstring& categoryId);
    
    /**
     * @brief 根据名称获取分类
     * @param name 分类名称
     */
    FileCategory* getCategoryByName(const std::wstring& name);
    
    /**
     * @brief 设置文件的分类
     * @param filePath 文件路径
     * @param categoryId 分类ID
     */
    bool setFileCategory(const std::wstring& filePath, const std::wstring& categoryId);
    
    /**
     * @brief 获取文件的分类
     * @param filePath 文件路径
     */
    std::wstring getFileCategory(const std::wstring& filePath) const;
    
    /**
     * @brief 移除文件的分类
     * @param filePath 文件路径
     */
    bool removeFileCategory(const std::wstring& filePath);
    
    /**
     * @brief 添加文件到分类（根据分类名称）
     * @param filePath 文件路径
     * @param categoryName 分类名称
     */
    bool addFileToCategory(const std::wstring& filePath, const std::wstring& categoryName);
    
    /**
     * @brief 从分类中移除文件（根据分类名称）
     * @param filePath 文件路径
     */
    bool removeFileFromCategory(const std::wstring& filePath);
    
    /**
     * @brief 获取指定分类下的所有文件路径
     * @param categoryId 分类ID
     */
    std::vector<std::wstring> getFilesByCategory(const std::wstring& categoryId) const;
    
    /**
     * @brief 创建默认分类
     */
    void createDefaultCategories();
    
    /**
     * @brief 获取默认分类ID
     */
    static std::wstring getDefaultCategoryId() { return L"default"; }
    
    /**
     * @brief 获取默认分类名称
     */
    static std::wstring getDefaultCategoryName() { return L"默认分类"; }
    
private:
    /**
     * @brief 确保配置文件目录存在
     */
    bool ensureConfigDirectory() const;
    
    /**
     * @brief 从文件路径生成标准化的路径
     */
    std::wstring normalizePath(const std::wstring& path) const;
};