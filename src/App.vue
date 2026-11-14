
<script setup lang="ts">
import { computed, ref } from 'vue'

type SchoolStatus = '正常' | '停用'

interface School {
  id: number
  name: string
  code: string
  address: string
  contact: string
  phone: string
  status: SchoolStatus
  createdAt: string
}

const activePage = ref('schools')
const searchText = ref('')
const statusFilter = ref('全部')
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
    items: [{ id: 'settings', label: '系统设置', icon: '⚙' }],
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
  { icon: '＋', color: 'blue', title: '新设备已添加', description: '一台新设备已加入管理系统', time: '10 分钟前' },
  { icon: '✉', color: 'green', title: '消息发送完成', description: '一条班级通知已成功发送', time: '35 分钟前' },
  { icon: '♙', color: 'purple', title: '成员信息已更新', description: '成员资料发生了变更', time: '2 小时前' },
  { icon: '▤', color: 'orange', title: '班级信息已创建', description: '新的班级信息已添加', time: '昨天' },
]

const statistics = [
  { label: '学校总数', value: '12', change: '管理中的学校', icon: '⌂', color: 'blue' },
  { label: '班级总数', value: '86', change: '已创建的班级', icon: '▤', color: 'purple' },
  { label: '设备总数', value: '248', change: '已登记的设备', icon: '▣', color: 'green' },
  { label: '消息总数', value: '1,024', change: '累计发送消息', icon: '✉', color: 'orange' },
]

const schools = ref<School[]>([
  {
    id: 1,
    name: '第一实验学校',
    code: 'SCH-0001',
    address: '北京市海淀区',
    contact: '张老师',
    phone: '13800000001',
    status: '正常',
    createdAt: '2026-10-12',
  },
  {
    id: 2,
    name: '阳光中学',
    code: 'SCH-0002',
    address: '北京市朝阳区',
    contact: '李老师',
    phone: '13800000002',
    status: '正常',
    createdAt: '2026-10-15',
  },
  {
    id: 3,
    name: '育才小学',
    code: 'SCH-0003',
    address: '上海市浦东新区',
    contact: '王老师',
    phone: '13800000003',
    status: '正常',
    createdAt: '2026-10-20',
  },
  {
    id: 4,
    name: '启明学校',
    code: 'SCH-0004',
    address: '杭州市西湖区',
    contact: '陈老师',
    phone: '13800000004',
    status: '停用',
    createdAt: '2026-10-25',
  },
  {
    id: 5,
    name: '新城外国语学校',
    code: 'SCH-0005',
    address: '南京市鼓楼区',
    contact: '刘老师',
    phone: '13800000005',
    status: '正常',
    createdAt: '2026-11-01',
  },
])

const filteredSchools = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()

  return schools.value.filter((school) => {
    const matchesKeyword =
      !keyword ||
      [school.name, school.code, school.address, school.contact]
        .some((value) => value.toLowerCase().includes(keyword))

    const matchesStatus =
      statusFilter.value === '全部' || school.status === statusFilter.value

    return matchesKeyword && matchesStatus
  })
})

const activeSchoolCount = computed(
  () => schools.value.filter((school) => school.status === '正常').length,
)

const disabledSchoolCount = computed(
  () => schools.value.filter((school) => school.status === '停用').length,
)

const showSchoolDialog = ref(false)
const editingSchoolId = ref<number | null>(null)
const formError = ref('')

const schoolForm = ref({
  name: '',
  code: '',
  address: '',
  contact: '',
  phone: '',
  status: '正常' as SchoolStatus,
})

function selectPage(id: string) {
  activePage.value = id
  showNotifications.value = false
}

function handleQuickAction(id: string) {
  selectPage(id)
}

function resetForm() {
  schoolForm.value = {
    name: '',
    code: '',
    address: '',
    contact: '',
    phone: '',
    status: '正常',
  }
  formError.value = ''
  editingSchoolId.value = null
}

function openCreateDialog() {
  resetForm()
  showSchoolDialog.value = true
}

function openEditDialog(school: School) {
  editingSchoolId.value = school.id
  schoolForm.value = {
    name: school.name,
    code: school.code,
    address: school.address,
    contact: school.contact,
    phone: school.phone,
    status: school.status,
  }
  formError.value = ''
  showSchoolDialog.value = true
}

function closeDialog() {
  showSchoolDialog.value = false
  resetForm()
}

function saveSchool() {
  const form = schoolForm.value

  if (!form.name.trim()) {
    formError.value = '请输入学校名称'
    return
  }

  if (!form.code.trim()) {
    formError.value = '请输入学校代码'
    return
  }

  const duplicateCode = schools.value.some(
    (school) =>
      school.code.toLowerCase() === form.code.trim().toLowerCase() &&
      school.id !== editingSchoolId.value,
  )

  if (duplicateCode) {
    formError.value = '该学校代码已存在，请更换一个代码'
    return
  }

  if (editingSchoolId.value !== null) {
    const index = schools.value.findIndex(
      (school) => school.id === editingSchoolId.value,
    )

    if (index !== -1) {
      schools.value[index] = {
        ...schools.value[index],
        ...form,
        name: form.name.trim(),
        code: form.code.trim(),
        address: form.address.trim(),
        contact: form.contact.trim(),
        phone: form.phone.trim(),
      }
    }
  } else {
    schools.value.unshift({
      id: Math.max(0, ...schools.value.map((school) => school.id)) + 1,
      ...form,
      name: form.name.trim(),
      code: form.code.trim(),
      address: form.address.trim(),
      contact: form.contact.trim(),
      phone: form.phone.trim(),
      createdAt: new Date().toISOString().slice(0, 10),
    })
  }

  closeDialog()
}

function deleteSchool(school: School) {
  const confirmed = window.confirm(`确定删除学校“${school.name}”吗？此操作无法撤销。`)

  if (!confirmed) return

  schools.value = schools.value.filter((item) => item.id !== school.id)
}
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
        <section v-for="group in navigation" :key="group.title" class="nav-group">
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
            <input v-model="searchText" type="search" placeholder="搜索学校..." />
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
            <article v-for="item in statistics" :key="item.label" class="stat-card">
              <div class="stat-top">
                <span class="stat-label">{{ item.label }}</span>
                <span class="stat-icon" :class="item.color">{{ item.icon }}</span>
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

              <div class="activity-list">
                <div v-for="activity in activities" :key="activity.title" class="activity-item">
                  <div class="activity-icon" :class="activity.color">{{ activity.icon }}</div>
                  <div class="activity-content">
                    <strong>{{ activity.title }}</strong>
                    <span>{{ activity.description }}</span>
                  </div>
                  <time>{{ activity.time }}</time>
                </div>
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
                <button class="quick-action" @click="handleQuickAction('schools')">
                  <span class="quick-icon blue">⌂</span>
                  <span><strong>学校管理</strong><small>管理学校信息</small></span>
                  <span class="quick-arrow">→</span>
                </button>
                <button class="quick-action" @click="handleQuickAction('classrooms')">
                  <span class="quick-icon purple">▤</span>
                  <span><strong>班级管理</strong><small>查看班级信息</small></span>
                  <span class="quick-arrow">→</span>
                </button>
                <button class="quick-action" @click="handleQuickAction('devices')">
                  <span class="quick-icon green">▣</span>
                  <span><strong>设备管理</strong><small>管理已登记设备</small></span>
                  <span class="quick-arrow">→</span>
                </button>
                <button class="quick-action" @click="handleQuickAction('messages')">
                  <span class="quick-icon orange">✉</span>
                  <span><strong>消息中心</strong><small>查看消息记录</small></span>
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

        <template v-else-if="activePage === 'schools'">
          <section class="page-heading">
            <div>
              <p class="eyebrow">组织与基础信息</p>
              <h1>学校管理</h1>
              <p class="welcome-description">管理接入 CampusRelay 的学校信息。</p>
            </div>
            <button class="primary-button" @click="openCreateDialog">
              <span>＋</span> 添加学校
            </button>
          </section>

          <section class="school-summary">
            <article class="summary-card">
              <span class="summary-icon blue">⌂</span>
              <div><span>学校总数</span><strong>{{ schools.length }}</strong></div>
            </article>
            <article class="summary-card">
              <span class="summary-icon green">✓</span>
              <div><span>正常运行</span><strong>{{ activeSchoolCount }}</strong></div>
            </article>
            <article class="summary-card">
              <span class="summary-icon orange">Ⅱ</span>
              <div><span>已停用</span><strong>{{ disabledSchoolCount }}</strong></div>
            </article>
          </section>

          <section class="panel school-panel">
            <div class="panel-header school-panel-header">
              <div>
                <h2>学校列表</h2>
                <p>当前共有 {{ schools.length }} 所学校</p>
              </div>

              <div class="table-filters">
                <label class="filter-search">
                  <span>⌕</span>
                  <input v-model="searchText" type="search" placeholder="搜索名称、代码或联系人" />
                </label>
                <select v-model="statusFilter" aria-label="学校状态筛选">
                  <option>全部</option>
                  <option>正常</option>
                  <option>停用</option>
                </select>
              </div>
            </div>

            <div class="table-scroll">
              <table class="school-table">
                <thead>
                  <tr>
                    <th>学校信息</th>
                    <th>学校代码</th>
                    <th>所在地区</th>
                    <th>联系人</th>
                    <th>联系电话</th>
                    <th>状态</th>
                    <th>创建日期</th>
                    <th class="action-heading">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="school in filteredSchools" :key="school.id">
                    <td>
                      <div class="school-name-cell">
                        <span class="school-avatar">{{ school.name.slice(0, 1) }}</span>
                        <strong>{{ school.name }}</strong>
                      </div>
                    </td>
                    <td><span class="school-code">{{ school.code }}</span></td>
                    <td>{{ school.address || '—' }}</td>
                    <td>{{ school.contact || '—' }}</td>
                    <td>{{ school.phone || '—' }}</td>
                    <td>
                      <span class="status-pill" :class="school.status === '正常' ? 'status-active' : 'status-disabled'">
                        <i></i>{{ school.status }}
                      </span>
                    </td>
                    <td>{{ school.createdAt }}</td>
                    <td>
                      <div class="row-actions">
                        <button class="table-action" @click="openEditDialog(school)">编辑</button>
                        <button class="table-action danger" @click="deleteSchool(school)">删除</button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="filteredSchools.length === 0">
                    <td colspan="8" class="table-empty">
                      <span class="empty-icon">⌕</span>
                      <strong>没有找到符合条件的学校</strong>
                      <span>请尝试修改搜索内容或筛选条件</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="table-footer">
              <span>显示 {{ filteredSchools.length }} 条记录，共 {{ schools.length }} 所学校</span>
              <span>演示数据</span>
            </div>
          </section>
        </template>

        <section v-else class="placeholder-page">
          <div class="placeholder-icon">▦</div>
          <p class="eyebrow">工作空间</p>
          <h1>{{ currentTitle }}</h1>
          <p>该功能模块正在规划中，后续将在这里提供完整的管理功能。</p>
          <button class="primary-button" @click="selectPage('overview')">返回总览</button>
        </section>
      </div>
    </main>

    <div v-if="showSchoolDialog" class="modal-backdrop" @click.self="closeDialog">
      <section class="school-dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title">
        <header class="dialog-header">
          <div>
            <h2 id="dialog-title">{{ editingSchoolId === null ? '添加学校' : '编辑学校' }}</h2>
            <p>填写学校的基本信息</p>
          </div>
          <button class="dialog-close" aria-label="关闭" @click="closeDialog">×</button>
        </header>

        <form class="school-form" @submit.prevent="saveSchool">
          <label class="form-field">
            <span>学校名称 <i>*</i></span>
            <input v-model="schoolForm.name" placeholder="请输入学校名称" maxlength="80" />
          </label>

          <label class="form-field">
            <span>学校代码 <i>*</i></span>
            <input v-model="schoolForm.code" placeholder="例如：SCH-0006" maxlength="40" />
          </label>

          <label class="form-field">
            <span>所在地区</span>
            <input v-model="schoolForm.address" placeholder="请输入学校所在地区" maxlength="120" />
          </label>

          <div class="form-row">
            <label class="form-field">
              <span>联系人</span>
              <input v-model="schoolForm.contact" placeholder="联系人姓名" maxlength="40" />
            </label>
            <label class="form-field">
              <span>联系电话</span>
              <input v-model="schoolForm.phone" placeholder="联系电话" maxlength="30" />
            </label>
          </div>

          <label class="form-field">
            <span>学校状态</span>
            <select v-model="schoolForm.status">
              <option value="正常">正常</option>
              <option value="停用">停用</option>
            </select>
          </label>

          <p v-if="formError" class="form-error">{{ formError }}</p>

          <footer class="dialog-footer">
            <button type="button" class="secondary-button" @click="closeDialog">取消</button>
            <button type="submit" class="primary-button">保存</button>
          </footer>
        </form>
      </section>
    </div>
  </div>
</template>
