import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '../layouts/AdminLayout.vue'
import AdminUserView from '../views/AdminUserView.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import DigitalHumanView from '../views/DigitalHumanView.vue'
import FeedbackReportView from '../views/FeedbackReportView.vue'
import FaqView from '../views/FaqView.vue'
import ImportJobDetailView from '../views/ImportJobDetailView.vue'
import ImportJobView from '../views/ImportJobView.vue'
import KnowledgeCorrectionTaskView from '../views/KnowledgeCorrectionTaskView.vue'
import KnowledgeDocumentDetailView from '../views/KnowledgeDocumentDetailView.vue'
import KnowledgeDocumentView from '../views/KnowledgeDocumentView.vue'
import OperationLogView from '../views/OperationLogView.vue'
import RouteTemplateView from '../views/RouteTemplateView.vue'
import ScenicAreaView from '../views/ScenicAreaView.vue'
import ScenicSpotDetailView from '../views/ScenicSpotDetailView.vue'
import ScenicSpotListView from '../views/ScenicSpotListView.vue'
import ServicePoiView from '../views/ServicePoiView.vue'
import SessionManagementView from '../views/SessionManagementView.vue'
import SettingsAiProviderView from '../views/SettingsAiProviderView.vue'
import { getDefaultRouteByRole, useAuthStore } from '../stores/auth'

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
            roles: ['super_admin', 'ops_admin'],
          },
        },
        {
          path: 'analytics/dashboard',
          component: DashboardView,
          meta: {
            title: '数据大屏',
            description: '查看热门景点与游客行为趋势。',
            roles: ['super_admin', 'ops_admin'],
          },
        },
        {
          path: 'scenic-areas',
          component: ScenicAreaView,
          meta: {
            title: '景区管理',
            description: '维护景区主数据。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'scenic-spots',
          component: ScenicSpotListView,
          meta: {
            title: '景点管理',
            description: '维护景点列表并进入详情页。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'scenic-spots/:id',
          component: ScenicSpotDetailView,
          meta: {
            title: '景点详情',
            description: '更新景点基础信息与开放状态。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'service-pois',
          component: ServicePoiView,
          meta: {
            title: '便民服务点',
            description: '维护厕所、游客中心、餐饮、停车等服务点坐标。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'route-templates',
          component: RouteTemplateView,
          meta: {
            title: '路线模板',
            description: '维护路线模板并预览推荐结果。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'knowledge/documents',
          component: KnowledgeDocumentView,
          meta: {
            title: '知识管理',
            description: '维护知识文档并查看分块详情。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'knowledge/correction-tasks',
          component: KnowledgeCorrectionTaskView,
          meta: {
            title: '知识修正任务',
            description: '跟踪未命中问题到 FAQ 或文档修正结果的闭环。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'knowledge/documents/:id',
          component: KnowledgeDocumentDetailView,
          meta: {
            title: '知识文档详情',
            description: '查看文档内容与知识分块。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'knowledge/faqs',
          component: FaqView,
          meta: {
            title: 'FAQ 管理',
            description: '维护高频问题与标准答案。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'sessions',
          component: SessionManagementView,
          meta: {
            title: '会话记录与问题修正',
            description: '查看会话记录、未命中问题并推进知识修正闭环。',
            roles: ['super_admin', 'content_admin', 'ops_admin'],
          },
        },
        {
          path: 'imports',
          component: ImportJobView,
          meta: {
            title: '数据导入',
            description: '触发导入任务并查看任务列表。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'feedback-report',
          component: FeedbackReportView,
          meta: {
            title: '游客感受度报告',
            description: '查看满意度分布、平均评分与运营建议。',
            roles: ['super_admin', 'ops_admin'],
          },
        },
        {
          path: 'imports/:id',
          component: ImportJobDetailView,
          meta: {
            title: '导入任务详情',
            description: '查看导入任务结果与明细。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'digital-humans',
          component: DigitalHumanView,
          meta: {
            title: '数字人配置',
            description: '维护数字人欢迎语、音色和模式。',
            roles: ['super_admin', 'content_admin'],
          },
        },
        {
          path: 'settings/ai-providers',
          component: SettingsAiProviderView,
          meta: {
            title: 'AI 配置',
            description: '维护模型提供商配置。',
            roles: ['super_admin'],
          },
        },
        {
          path: 'settings/admin-users',
          component: AdminUserView,
          meta: {
            title: '账号管理',
            description: '管理后台账号、角色、状态和密码。',
            roles: ['super_admin'],
          },
        },
        {
          path: 'operation-logs',
          component: OperationLogView,
          meta: {
            title: '操作日志',
            description: '查看后台写操作审计记录。',
            roles: ['super_admin', 'ops_admin'],
          },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (to.path !== '/login' && !authStore.accessToken) {
    return '/login'
  }

  if (authStore.accessToken && !authStore.profileLoaded) {
    try {
      await authStore.fetchProfile()
    } catch (error) {
      authStore.clearAuth()
      return '/login'
    }
  }

  if (to.path === '/login' && authStore.accessToken) {
    return getDefaultRouteByRole(authStore.role)
  }

  const roles = to.meta.roles as string[] | undefined
  if (roles && authStore.role && !roles.includes(authStore.role)) {
    return getDefaultRouteByRole(authStore.role)
  }

  return true
})
