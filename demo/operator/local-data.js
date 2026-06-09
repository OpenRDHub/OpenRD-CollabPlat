window.OpenRDOperatorDemo = {
  role: {
    name: '运管 / 产品经理',
    user: '易然',
    platformId: 'ops_yiran',
    phone: '138****6205',
    definition: '运管也就是产品经理，负责审核需求、与需求者沟通、判断需求边界，并在信息充分时把需求转化为可被共建者承接的任务工单。'
  },
  flow: [
    '欢迎页',
    '登录',
    '社区首页',
    '运管工作台',
    '需求详情沟通',
    '转化任务',
    '任务详情追踪'
  ],
  demands: [
    {
      id: 'REQ-2418',
      title: '复诊问题清单与用药提醒',
      status: '沟通中',
      conversion: '待转化',
      owner: '易然',
      next: '信息充分，可转化为任务工单'
    },
    {
      id: 'REQ-2432',
      title: '自然语言病历摘要辅助',
      status: '沟通中',
      conversion: '待评估',
      owner: '易然',
      next: '等待需求者补充脱敏样例'
    }
  ],
  tasks: [],
  storageKey: 'openrd_operator_demo_state_v2',
  save() {
    localStorage.setItem(this.storageKey, JSON.stringify({
      role: this.role,
      flow: this.flow,
      demands: this.demands,
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
      this.demands = parsed.demands || this.demands;
      this.tasks = parsed.tasks || this.tasks;
    } catch (error) {
      this.save();
    }
    return this;
  }
};

window.OpenRDOperatorDemo.load();
