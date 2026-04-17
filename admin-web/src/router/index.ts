import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '../layouts/AdminLayout.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import DigitalHumanView from '../views/DigitalHumanView.vue'
import FeedbackReportView from '../views/FeedbackReportView.vue'
import FaqView from '../views/FaqView.vue'
import ImportJobDetailView from '../views/ImportJobDetailView.vue'
import ImportJobView from '../views/ImportJobView.vue'
import KnowledgeDocumentDetailView from '../views/KnowledgeDocumentDetailView.vue'
import KnowledgeDocumentView from '../views/KnowledgeDocumentView.vue'
import OperationLogView from '../views/OperationLogView.vue'
import ScenicAreaView from '../views/ScenicAreaView.vue'
import ScenicSpotDetailView from '../views/ScenicSpotDetailView.vue'
import ScenicSpotListView from '../views/ScenicSpotListView.vue'
import SettingsAiProviderView from '../views/SettingsAiProviderView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    {
      path: '/',
      component: AdminLayout,
      children: [
        {
          path: '',
          component: DashboardView,
          meta: {
            title: '运营概览',
            description: '查看事件量、知识文档、景点数据与导入任务概览。',
          },
        },
        {
          path: 'analytics/dashboard',
          component: DashboardView,
          meta: {
            title: '数据大屏',
            description: '查看热门景点与游客行为趋势。',
          },
        },
        {
          path: 'scenic-areas',
          component: ScenicAreaView,
          meta: {
            title: '景区管理',
            description: '维护景区主数据。',
          },
        },
        {
          path: 'scenic-spots',
          component: ScenicSpotListView,
          meta: {
            title: '景点管理',
            description: '维护景点列表并进入详情页。',
          },
        },
        {
          path: 'scenic-spots/:id',
          component: ScenicSpotDetailView,
          meta: {
            title: '景点详情',
            description: '更新景点基础信息与开放状态。',
          },
        },
        {
          path: 'knowledge/documents',
          component: KnowledgeDocumentView,
          meta: {
            title: '知识管理',
            description: '维护知识文档并查看分块详情。',
          },
        },
        {
          path: 'knowledge/documents/:id',
          component: KnowledgeDocumentDetailView,
          meta: {
            title: '知识文档详情',
            description: '查看文档内容与知识分块。',
          },
        },
        {
          path: 'knowledge/faqs',
          component: FaqView,
          meta: {
            title: 'FAQ 管理',
            description: '维护高频问题与标准答案。',
          },
        },
        {
          path: 'imports',
          component: ImportJobView,
          meta: {
            title: '数据导入',
            description: '触发导入任务并查看任务列表。',
          },
        },
        {
          path: 'feedback-report',
          component: FeedbackReportView,
          meta: {
            title: '游客感受度报告',
            description: '查看满意度分布、平均评分与运营建议。',
          },
        },
        {
          path: 'imports/:id',
          component: ImportJobDetailView,
          meta: {
            title: '导入任务详情',
            description: '查看导入任务结果与明细。',
          },
        },
        {
          path: 'digital-humans',
          component: DigitalHumanView,
          meta: {
            title: '数字人配置',
            description: '维护数字人欢迎语、音色和模式。',
          },
        },
        {
          path: 'settings/ai-providers',
          component: SettingsAiProviderView,
          meta: {
            title: 'AI 配置',
            description: '维护模型提供商配置。',
          },
        },
        {
          path: 'operation-logs',
          component: OperationLogView,
          meta: {
            title: '操作日志',
            description: '查看后台写操作审计记录。',
          },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('accessToken')
  if (to.path !== '/login' && !token) {
    return '/login'
  }
  if (to.path === '/login' && token) {
    return '/'
  }
  return true
})
