import Vue from 'vue'
import Router from 'vue-router'
import VueDemo from '@/components/VueDemo'
import Search from '@/components/Search'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: VueDemo
    },
    {
      path: '/search',
      name: 'search',
      component: Search
    }
  ]
})
