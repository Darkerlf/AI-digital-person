<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { guardCurrentPage, installAuthNavigationGuards } from './utils/authGuard'

onLaunch(() => {
  console.log('App Launch')
  installAuthNavigationGuards()
  setTimeout(() => guardCurrentPage(), 0)
})

onShow(() => {
  console.log('App Show')
  setTimeout(() => guardCurrentPage(), 0)
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style>
page {
  --guide-primary: #238fa3;
  --guide-primary-dark: #2aaec0;
  --guide-primary-soft: #e9fbf7;
  --guide-accent: #b4533c;
  --guide-accent-soft: #fff1ea;
  --guide-ink: #17252b;
  --guide-muted: #64747d;
  --guide-line: #d7edf0;
  --guide-paper: #f7fdfb;
  --guide-card: #ffffff;
  --guide-shadow: 0 12rpx 34rpx rgba(35, 143, 163, 0.09);
  background-color: #f7fdfb;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #17252b;
  font-size: 28rpx;
}

view,
text,
input,
textarea,
button {
  box-sizing: border-box;
}

button {
  margin: 0;
  padding: 0;
  line-height: 1;
  background: transparent;
}

button::after {
  border: none;
}
</style>
