#!/bin/bash
# feature/demand-submit 提交脚本

cd "$(dirname "$0")"

echo "=================================="
echo "feature/demand-submit 代码提交"
echo "=================================="
echo ""

# 显示文件状态
echo "📦 文件变更："
git status --short

echo ""
echo "📝 提交信息预览："
echo "-----------------------------------"
cat << 'EOF'
feat(demands): 完成需求提交弹窗和我的需求列表页

## 功能实现

### 1. 需求提交弹窗 (DemandSubmitDialog.vue)
- 表单字段：标题、详情、联系电话、微信号
- 附件上传功能（文件列表展示和删除）
- 隐私确认复选框
- 表单验证（必填项、至少一个联系方式）
- 提交成功/失败 Toast 提示
- 完全复刻 demo 样式

### 2. 我的需求列表页 (MyDemandsView.vue)
- Hero 区域：标题、描述、焦点卡片
- 统计卡片网格：总数、待审核、已转任务、已关闭
- Tab 筛选：全部、待审核、沟通中、已转任务、已关闭
- 状态筛选下拉框和搜索框
- 表格展示：需求详情、状态、进度条、操作按钮
- 分页功能
- 空状态和加载状态
- 响应式布局

### 3. 需求详情页占位 (DemandDetailView.vue)
- 基础页面结构（后续迭代完善）

### 4. API 接口和类型定义
- demandsApi.submit() - 提交需求
- demandsApi.getMyDemands() - 获取我的需求列表
- TypeScript 类型：DemandSubmitPayload, MyDemand

### 5. Mock 数据配置
- 5 条模拟需求数据（覆盖各种状态）
- MSW Handler 支持提交、查询、筛选、搜索、分页

### 6. 路由和集成
- 新增 /my-demands 和 /demands/:id 路由
- Dashboard 集成"提需求"和"我的需求"按钮

### 7. Bug 修复
- 修复 OrdToast 组件的 $emit 使用错误

## 技术规范

- ✅ 严格使用 OrdUI 组件库（禁止第三方 UI 库）
- ✅ scoped CSS + CSS 变量（无硬编码颜色）
- ✅ 完全复刻 demo 原型设计（Webflow 风格）
- ✅ 响应式布局（992px、768px 断点）
- ✅ TypeScript 类型安全

## 参考文档

- demo/all-pages/home.html（需求提交弹窗）
- demo/all-pages/my-demands.html（我的需求列表）
- frontend/CLAUDE.md（开发规范）
- docs/前端后端开发任务分配计划.md（Sprint 1 第 3 周）
EOF
echo "-----------------------------------"
echo ""

# 询问是否提交
read -p "是否执行 git commit？(y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    git commit -F - << 'EOF'
feat(demands): 完成需求提交弹窗和我的需求列表页

## 功能实现

### 1. 需求提交弹窗 (DemandSubmitDialog.vue)
- 表单字段：标题、详情、联系电话、微信号
- 附件上传功能（文件列表展示和删除）
- 隐私确认复选框
- 表单验证（必填项、至少一个联系方式）
- 提交成功/失败 Toast 提示
- 完全复刻 demo 样式

### 2. 我的需求列表页 (MyDemandsView.vue)
- Hero 区域：标题、描述、焦点卡片
- 统计卡片网格：总数、待审核、已转任务、已关闭
- Tab 筛选：全部、待审核、沟通中、已转任务、已关闭
- 状态筛选下拉框和搜索框
- 表格展示：需求详情、状态、进度条、操作按钮
- 分页功能
- 空状态和加载状态
- 响应式布局

### 3. 需求详情页占位 (DemandDetailView.vue)
- 基础页面结构（后续迭代完善）

### 4. API 接口和类型定义
- demandsApi.submit() - 提交需求
- demandsApi.getMyDemands() - 获取我的需求列表
- TypeScript 类型：DemandSubmitPayload, MyDemand

### 5. Mock 数据配置
- 5 条模拟需求数据（覆盖各种状态）
- MSW Handler 支持提交、查询、筛选、搜索、分页

### 6. 路由和集成
- 新增 /my-demands 和 /demands/:id 路由
- Dashboard 集成"提需求"和"我的需求"按钮

### 7. Bug 修复
- 修复 OrdToast 组件的 $emit 使用错误

## 技术规范

- ✅ 严格使用 OrdUI 组件库（禁止第三方 UI 库）
- ✅ scoped CSS + CSS 变量（无硬编码颜色）
- ✅ 完全复刻 demo 原型设计（Webflow 风格）
- ✅ 响应式布局（992px、768px 断点）
- ✅ TypeScript 类型安全

## 参考文档

- demo/all-pages/home.html（需求提交弹窗）
- demo/all-pages/my-demands.html（我的需求列表）
- frontend/CLAUDE.md（开发规范）
- docs/前端后端开发任务分配计划.md（Sprint 1 第 3 周）
EOF

    echo ""
    echo "✅ 提交完成！"
    echo ""
    echo "下一步："
    echo "1. 推送到远程：git push origin feature/demand-submit"
    echo "2. 在 GitHub 创建 Pull Request"
    echo ""
else
    echo ""
    echo "⏸️  取消提交"
    echo ""
    echo "手动提交命令："
    echo "git commit -m \"feat(demands): 完成需求提交弹窗和我的需求列表页\""
    echo ""
fi
