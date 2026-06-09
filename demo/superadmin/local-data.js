window.OpenRDSuperAdminDemo = {
  role: {
    name: '超级管理员',
    user: '顾星河',
    platformId: 'admin_guxinghe',
    phone: '136****9001',
    definition: '超级管理员负责平台全局治理：用户生命周期、角色权限、系统审计、任务与需求运营总览，并为运管和共建者提供安全可追溯的协作环境。'
  },
  flow: [
    '欢迎页',
    '登录',
    '社区首页',
    '超级管理员工作台',
    '用户管理',
    '权限管理',
    '系统日志',
    '任务与需求治理'
  ],
  governance: {
    activeUsers: 148,
    pendingRiskEvents: 5,
    manualPermissionGrants: 12,
    auditEvents: 86
  },
  storageKey: 'openrd_superadmin_demo_state_v1',
  save() {
    localStorage.setItem(this.storageKey, JSON.stringify({
      role: this.role,
      flow: this.flow,
      governance: this.governance,
      savedAt: new Date().toISOString()
    }));
  },
  load() {
    const raw = localStorage.getItem(this.storageKey);
    if (!raw) {
      this.save();
      return this;
    }
    try {
      const parsed = JSON.parse(raw);
      this.role = parsed.role || this.role;
      this.flow = parsed.flow || this.flow;
      this.governance = parsed.governance || this.governance;
    } catch (error) {
      this.save();
    }
    return this;
  }
};

window.OpenRDSuperAdminDemo.load();
