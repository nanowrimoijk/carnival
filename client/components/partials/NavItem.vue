<template>
  <li class="navitem-wrapper">
    <nuxt-link :to="to" class="navitem-link">
      <div @click="shrinkHeader" class="navitem">
        <h2>{{ name }}</h2>
      </div>
    </nuxt-link>
  </li>
</template>

<script>
import anime from 'animejs';

export default {
  props: {
    name: {
      type: String,
      default: () => 'Link Name'
    },
    to: {
      type: String,
      default: () => '/unresolved-link'
    }
  },
  methods: {
    // to do - keep dry and not copy paste from Heading.vue
    shrinkHeader() {
      anime({
        targets: '.header-wrapper-wrapper',
        translateX: 10,
        translateY: 10,
        easing: 'spring(1, 100, 90, 10)'
      });

      anime({
        targets: '.header-wrapper',
        translateX: 0,
        translateY: 0,
        rotateY: '0deg',
        width: 190,
        height: 60,
        easing: 'spring(1, 100, 90, 8)'
      });
    }
  }
};
</script>

<style lang="postcss" scoped>
.navitem-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.navitem-link {
  display: block;
  color: $text;
  text-decoration: none;
}

.navitem {
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;

  background-color: $bg-light;
  transition: all 0.3s ease-out;
  list-style-type: none;
}
</style>
