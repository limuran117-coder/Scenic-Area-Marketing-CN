// 银基动物王国小红书搜索 - 直接通过CDP导航
async (cdp_url) => {
  const browser = await p.chromium.connect_over_cdp(cdp_url);
  const ctx = browser.contexts[0];
  let page = null;
  for (const pg of ctx.pages) {
    if (pg.url && pg.url.includes('xiaohongshu.com')) { page = pg; break; }
  }
  if (!page) page = await ctx.new_page();
  await page.goto('https://www.xiaohongshu.com/search_result?keyword=' + encodeURIComponent('银基动物王国'));
  await page.waitForTimeout(5000);
  const text = await page.evaluate(() => document.body.innerText);
  return text.substring(0, 3000);
}
