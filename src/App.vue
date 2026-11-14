<script setup lang="ts">
import { computed, ref } from 'vue'

const activePage = ref('overview')
const searchText = ref('')
const showNotifications = ref(false)

const navigation = [
  {
    title: '工作空间',
    items: [
      { id: 'overview', label: '总览', icon: '▦' },
      { id: 'schools', label: '学校管理', icon: '⌂' },
      { id: 'classrooms', label: '班级管理', icon: '▤' },
      { id: 'devices', label: '设备管理', icon: '▣' },
    ],
  },
  {
    title: '沟通与管理',
    items: [
      { id: 'messages', label: '消息中心', icon: '✉' },
      { id: 'members', label: '成员管理', icon: '♙' },
    ],
  },
  {
    title: '系统',
    items: [
      { id: 'settings', label: '系统设置', icon: '⚙' },
    ],
  },
]

const pageTitles: Record<string, string> = {
  overview: '总览',
  schools: '学校管理',
  classrooms: '班级管理',
  devices: '设备管理',
  messages: '消息中心',
  members: '成员管理',
  settings: '系统设置',
}

const currentTitle = computed(() => pageTitles[activePage.value] ?? '总览')

const activities = [
  {
    icon: '＋',
    color: 'blue',
    title: '新设备已添加',
    description: '一台新设备已加入管理系统',
    time: '10 分钟前',
  },
  {
    icon: '✉',
    color: 'green',
    title: '消息发送完成',
    description: '一条班级通知已成功发送',
    time: '35 分钟前',
  },
  {
    icon: '♙',
    color: 'purple',
    title: '成员信息已更新',
    description: '成员资料发生了变更',
    time: '2 小时前',
  },
  {
    icon: '▤',
    color: 'orange',
    title: '班级信息已创建',
    description: '新的班级信息已添加',
    time: '昨天',
  },
]

const statistics = [
  { label: '学校总数', value: '12', change: '管理中的学校', icon: '⌂', color: 'blue' },
  { label: '班级总数', value: '86', change: '已创建的班级', icon: '▤', color: 'purple' },
  { label: '设备总数', value: '248', change: '已登记的设备', icon: '▣', color: 'green' },
  { label: '消息总数', value: '1,024', change: '累计发送消息', icon: '✉', color: 'orange' },
]

function selectPage(id: string) {
  activePage.value = id
  showNotifications.value = false
}

function handleQuickAction(id: string) {
  selectPage(id)
}

const filteredActivities = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  if (!keyword) return activities

  return activities.filter((activity) =>
    `${activity.title} ${activity.description}`.toLowerCase().includes(keyword),
  )
})
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-logo">C</div>
        <div class="brand-text">
          <strong>CampusRelay</strong>
          <span>校园协作管理平台</span>
        </div>
      </div>

      <div class="workspace-label">工作空间</div>

      <nav class="navigation">
        <section
          v-for="group in navigation"
          :key="group.title"
          class="nav-group"
        >
          <p class="nav-heading">{{ group.title }}</p>

          <button
            v-for="item in group.items"
            :key="item.id"
            class="nav-item"
            :class="{ active: activePage === item.id }"
            @click="selectPage(item.id)"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
            <span v-if="item.id === 'messages'" class="nav-count">3</span>
          </button>
        </section>
      </nav>

      <div class="sidebar-bottom">
        <div class="help-card">
          <div class="help-icon">?</div>
          <div>
            <strong>需要帮助？</strong>
            <span>查看使用说明</span>
          </div>
          <span class="help-arrow">→</span>
        </div>

        <div class="sidebar-user">
          <div class="avatar">A</div>
          <div class="user-info">
            <strong>管理员</strong>
            <span>系统管理员</span>
          </div>
          <span class="user-more">···</span>
        </div>
      </div>
    </aside>

    <main class="main-area">
      <header class="topbar">
        <div class="breadcrumb">
          <span>CampusRelay</span>
          <span class="breadcrumb-separator">/</span>
          <strong>{{ currentTitle }}</strong>
        </div>

        <div class="topbar-actions">
          <label class="search-box">
            <span>⌕</span>
            <input
              v-model="searchText"
              type="search"
              placeholder="搜索动态..."
            />
            <kbd>⌘ K</kbd>
          </label>

          <div class="notification-wrapper">
            <button
              class="icon-button notification-button"
              aria-label="通知"
              @click="showNotifications = !showNotifications"
            >
              ♧
              <span class="notification-dot"></span>
            </button>

            <div v-if="showNotifications" class="notification-popover">
              <strong>通知</strong>
              <p>目前没有新的通知。</p>
            </div>
          </div>

          <div class="topbar-divider"></div>

          <div class="topbar-profile">
            <div class="avatar small">A</div>
            <div class="topbar-user-info">
              <strong>管理员</strong>
              <span>Administrator</span>
            </div>
            <span class="profile-chevron">⌄</span>
          </div>
        </div>
      </header>

      <div class="page-content">
        <template v-if="activePage === 'overview'">
          <section class="welcome-section">
            <div>
              <p class="eyebrow">工作空间概览</p>
              <h1>欢迎回来，管理员</h1>
              <p class="welcome-description">
                这里是 CampusRelay 的管理中心，查看校园管理情况和近期动态。
              </p>
            </div>

            <div class="welcome-date">
              <span class="date-icon">◷</span>
              <span>管理控制台</span>
            </div>
          </section>

          <section class="statistics-grid">
            <article
              v-for="item in statistics"
              :key="item.label"
              class="stat-card"
            >
              <div class="stat-top">
                <span class="stat-label">{{ item.label }}</span>
                <span class="stat-icon" :class="item.color">
                  {{ item.icon }}
                </span>
              </div>
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-description">{{ item.change }}</div>
            </article>
          </section>

          <section class="content-grid">
            <article class="panel activity-panel">
              <div class="panel-header">
                <div>
                  <h2>近期动态</h2>
                  <p>查看工作空间最近发生的操作</p>
                </div>
                <button class="text-button" @click="selectPage('messages')">
                  查看全部 <span>→</span>
                </button>
              </div>

              <div v-if="filteredActivities.length" class="activity-list">
                <div
                  v-for="activity in filteredActivities"
                  :key="activity.title"
                  class="activity-item"
                >
                  <div class="activity-icon" :class="activity.color">
                    {{ activity.icon }}
                  </div>
                  <div class="activity-content">
                    <strong>{{ activity.title }}</strong>
                    <span>{{ activity.description }}</span>
                  </div>
                  <time>{{ activity.time }}</time>
                </div>
              </div>

              <div v-else class="empty-state">
                没有找到匹配的动态
              </div>
            </article>

            <article class="panel quick-panel">
              <div class="panel-header">
                <div>
                  <h2>快捷入口</h2>
                  <p>快速进入常用管理功能</p>
                </div>
              </div>

              <div class="quick-actions">
                <button
                  class="quick-action"
                  @click="handleQuickAction('schools')"
                >
                  <span class="quick-icon blue">⌂</span>
                  <span>
                    <strong>学校管理</strong>
                    <small>管理学校信息</small>
                  </span>
                  <span class="quick-arrow">→</span>
                </button>

                <button
                  class="quick-action"
                  @click="handleQuickAction('classrooms')"
                >
                  <span class="quick-icon purple">▤</span>
                  <span>
                    <strong>班级管理</strong>
                    <small>查看班级信息</small>
                  </span>
                  <span class="quick-arrow">→</span>
                </button>

                <button
                  class="quick-action"
                  @click="handleQuickAction('devices')"
                >
                  <span class="quick-icon green">▣</span>
                  <span>
                    <strong>设备管理</strong>
                    <small>管理已登记设备</small>
                  </span>
                  <span class="quick-arrow">→</span>
                </button>

                <button
                  class="quick-action"
                  @click="handleQuickAction('messages')"
                >
                  <span class="quick-icon orange">✉</span>
                  <span>
                    <strong>消息中心</strong>
                    <small>查看消息记录</small>
                  </span>
                  <span class="quick-arrow">→</span>
                </button>
              </div>
            </article>
          </section>

          <footer class="page-footer">
            <span>CampusRelay</span>
            <span>校园协作管理平台</span>
          </footer>
        </template>

        <section v-else class="placeholder-page">
          <div class="placeholder-icon">▦</div>
          <p class="eyebrow">工作空间</p>
          <h1>{{ currentTitle }}</h1>
          <p>该功能模块正在规划中，后续将在这里提供完整的管理功能。</p>
          <button class="primary-button" @click="selectPage('overview')">
            返回总览
          </button>
        </section>
      </div>
    </main>
  </div>
</template>