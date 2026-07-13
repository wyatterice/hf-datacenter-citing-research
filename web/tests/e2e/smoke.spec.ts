import { test, expect } from '@playwright/test'

test.describe('datacenter impact tool', () => {
  test('loads with header, controls, and four score cards', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Datacenter Impact Research Tool' })).toBeVisible()

    // Defaults to the first state/county; the scores section renders four
    // dimension cards.
    const cards = page.locator('#scores .chart-card')
    await expect(cards).toHaveCount(4)
    for (const label of ['Energy', 'Land', 'Broadband', 'Water']) {
      await expect(page.locator('#scores .card-header', { hasText: label })).toBeVisible()
    }
  })

  test('benchmark toggle changes the percentile label', async ({ page }) => {
    await page.goto('/')
    const header = page.locator('#scores .metrics-section-header h3')
    await expect(header).toContainText('vs. counties where hyperscalers have built')

    await page.getByRole('radio', { name: 'All US Counties' }).click()
    await expect(header).toContainText('vs. all US counties')
  })

  test('estimator computes the deterministic 50 MW default outputs', async ({ page }) => {
    await page.goto('/')
    const demand = page.locator('#demand')
    await expect(demand).toBeVisible()

    // 50 MW IT load x PUE 1.30 = 65 MW grid draw.
    await expect(
      demand.locator('.chart-card', { hasText: 'Energy demand' }).locator('.impact-number'),
    ).toHaveText('65')
  })

  test('floating nav exposes the four section links', async ({ page }) => {
    await page.goto('/')
    const nav = page.locator('.floating-nav')
    await expect(nav).toBeVisible()
    for (const label of ['Scores', 'Demand', 'Economics', 'Tax']) {
      await expect(nav.locator('.nav-item', { hasText: label })).toHaveCount(1)
    }
  })

  test('clicking a nav link scrolls to its section', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('#tax')).not.toBeInViewport()
    await page.locator('.nav-toggle').click()
    await page.locator('.nav-item', { hasText: 'Tax' }).click()
    await expect(page.locator('#tax')).toBeInViewport()
  })
})
