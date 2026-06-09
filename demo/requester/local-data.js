window.OpenRDRequesterDemo = {
  role: {
    name: '需求者',
    user: '陈北',
    platformId: 'requester_chenbei',
    phone: '159****7824',
    definition: '需求者是提出真实协作诉求的人，可以发布需求、补充材料、查看沟通进展，并在需求转为任务后持续追踪交付状态。'
  },
  flow: [
    '欢迎页',
    '登录',
    '需求者工作台',
    '发布需求',
    '我的需求',
    '需求详情沟通',
    '任务进展追踪',
    '消息与个人资料'
  ],
  demands: [
    {
      id: 'REQ-2418',
      title: '复诊问题清单与用药提醒',
      status: '沟通中',
      conversion: '待转化',
      owner: '易然',
      next: '产品经理已确认边界，可转化任务'
    },
    {
      id: 'REQ-2432',
      title: '自然语言病历摘要辅助',
      status: '沟通中',
      conversion: '待评估',
      owner: '易然 / 青禾',
      next: '等待补充脱敏样例'
    }
  ],
  storageKey: 'openrd_requester_demo_state',
  save() {
    localStorage.setItem(this.storageKey, JSON.stringify({
      role: this.role,
      flow: this.flow,
      demands: this.demands,
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
    } catch (error) {
      this.save();
    }
    return this;
  }
};

window.OpenRDRequesterDemo.load();
