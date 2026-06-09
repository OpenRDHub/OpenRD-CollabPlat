window.OpenRDBuilderDemo = {
  role: {
    name: '共建者',
    user: '林知行',
    platformId: 'openrd_linxing',
    phone: '136****4092',
    definition: '共建者是参与任务实现的人，可以浏览可参与任务、加入或管理队伍、处理自己负责的分工，并在任务详情中提交进展和查看需求来源。'
  },
  flow: [
    '欢迎页',
    '登录',
    '共建者工作台',
    '我的任务',
    '任务详情',
    '队伍详情',
    '分工与申请处理',
    '消息与个人资料'
  ],
  tasks: [
    {
      id: 'TASK-1042',
      title: '用药提醒 API 与消息队列联调',
      role: '技术评审 / 队长',
      status: '解决中',
      team: '补充招募',
      next: '补充接口字段与队列重试说明'
    },
    {
      id: 'TASK-1051',
      title: '自然语言病历摘要任务拆解',
      role: '数据脱敏边界评审',
      status: '待处理',
      team: '成员确认',
      next: '审核加入申请并确认模型评估方案'
    }
  ],
  storageKey: 'openrd_builder_demo_state',
  save() {
    localStorage.setItem(this.storageKey, JSON.stringify({
      role: this.role,
      flow: this.flow,
      tasks: this.tasks,
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
      this.tasks = parsed.tasks || this.tasks;
    } catch (error) {
      this.save();
    }
    return this;
  }
};

window.OpenRDBuilderDemo.load();
