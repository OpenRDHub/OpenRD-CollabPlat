import { authHandlers } from './auth'
import { userHandlers } from './user'
import { demandHandlers } from './demands'
import { taskHandlers } from './tasks'
import { messageHandlers } from './messages'
import { adminHandlers } from './admin'
import { fileHandlers } from './files'

export const handlers = [
  ...authHandlers,
  ...userHandlers,
  ...demandHandlers,
  ...taskHandlers,
  ...messageHandlers,
  ...adminHandlers,
  ...fileHandlers,
]
