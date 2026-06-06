import { describe, expect, it } from 'vitest'

import { router } from '../router'

describe('admin user route', () => {
  it('registers a super admin account management route', () => {
    const route = router.getRoutes().find((item) => item.path === '/settings/admin-users')

    expect(route).toBeDefined()
    expect(route?.meta.roles).toEqual(['super_admin'])
  })
})
