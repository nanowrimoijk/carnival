<template>
  <div class="error">
    <span class="emoji">🤪</span>
    <h1>{{ errorMessage }}</h1>
    <nuxt-link to="/" class="link">return home</nuxt-link>
  </div>
</template>

<script>
export default {
  props: {
    error: {
      type: Object,
      default: () => ({
        message: 'error'
      })
    }
  },
  data() {
    return {
      errorMessage:
        this.error.message === 'This page could not be found'
          ? 'oops! this page cannot be found'
          : this.error.message
    };
  }
};
</script>

<style scoped lang="postcss">
.error {
  padding: 100px;
  text-align: center;
}

.emoji {
  font-size: 10rem;
}

.link {
  display: inline-block;
  padding: 10px;
  margin: 20px;
  border-radius: 5px;
  background-color: $bg;
  text-decoration: none;
  color: white;
  font-size: 2rem;
  transition: background-color 100ms ease-in-out-quad;
}

.link:hover {
  background-color: color-mod($bg shade(50%));
  transition: background-color 100ms ease-in-out-quad;
}
</style>
