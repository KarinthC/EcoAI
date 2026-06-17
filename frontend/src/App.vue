<!-- frontend/src/App.vue -->
<script setup>
import ConnectionIndicator from './components/ConnectionIndicator.vue'
import UserIdentification from './components/UserIdentification.vue'

</script>


<template>
  <div id="app">
    <ConnectionIndicator />
    <UserIdentification/>
    <router-view />
  </div>
</template>