import { expect } from 'vitest'
import { sandboxTest } from './setup'

sandboxTest('cursor position', async ({ sandbox }) => {
  const pos = await sandbox.getCursorPosition()
  const size = await sandbox.getScreenSize()
  // By the default, the cursor's position is in the center of the screen
  expect(pos).toEqual({ x: size.width / 2, y: size.height / 2 })
})

sandboxTest('mouse move', async ({ sandbox }) => {
  await sandbox.moveMouse(100, 200)
  const pos2 = await sandbox.getCursorPosition()
  expect(pos2).toEqual({ x: 100, y: 200 })
})

sandboxTest('mouse left click', async ({ sandbox }) => {
  // TODO: Implement
})

sandboxTest('mouse double click', async ({ sandbox }) => {
  // TODO: Implement
})

sandboxTest('mouse right click', async ({ sandbox }) => {
  // TODO: Implement
})

sandboxTest('mouse middle click', async ({ sandbox }) => {
  // TODO: Implement
})

sandboxTest('mouse scroll', async ({ sandbox }) => {
  // TODO: Implement
})
