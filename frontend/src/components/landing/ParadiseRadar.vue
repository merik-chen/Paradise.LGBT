<template lang='pug'>
  #radar
</template>

<script>
const loadGoogleMapsAPI = require('load-google-maps-api')

export default {
  data() {
    const initData = {
      radar: null,
      marker: null,
    }

    return initData
  },
  methods: {
    getUserGeoInfo(callback) {
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition((position) => {
          callback(position.coords.latitude, position.coords.longitude)
        })
      }
    },
    initMaps(googleMaps) {
      const self = this
      self.getUserGeoInfo((lat, lng) => {
        const center = { lat, lng }
        self.radar = new googleMaps.Map(
        document.getElementById('radar'), {
          center,
          zoom: 18,
        })
        self.marker = new googleMaps.Marker({
          position: center,
          map: self.radar,
        })
      })
    },
  },
  created() {
    const self = this
    loadGoogleMapsAPI({
      // key: 'AIzaSyDFBy8_iLrMYSfTF5py7plQXBXilhYlt5Y',
    }).then((googleMaps) => {
      self.initMaps(googleMaps)
    })
  },
}
</script>

<style lang="sass">
  #radar
    width: 100%
    height: 100%
</style>
