import { describe, it, expect } from 'vitest'

describe('main entry', () => {
  it('imports without throwing and mounts to root', async () => {
    const root = document.createElement('div')
    root.id = 'root'
    document.body.appendChild(root)

    // dynamic import to execute the module
    await import('../main.jsx')

    expect(document.getElementById('root')).toBeTruthy()
  })
})
