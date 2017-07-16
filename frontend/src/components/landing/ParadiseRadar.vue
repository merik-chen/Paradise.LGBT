<template lang='pug'>
  #radar
</template>

<script>
import { StoreService } from '@/services/index'

const loadGoogleMapsAPI = require('load-google-maps-api')

const storeService = new StoreService()

export default {
  data() {
    const initData = {
      radar: null,
      marker: null,
      storeList: null,
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
          zoom: 20,
        })
        self.marker = new googleMaps.Marker({
          position: center,
          map: self.radar,
        })
        const storesData = storeService.searchByGeo(lat, lng)
        // self.storeList = storesData.stores
        // console.log(storesData)
        storesData.then((data) => {
          data.stores.forEach((store) => {
            const storeMaker = new googleMaps.Marker({
              position: {
                lat: store.geospatial.lat,
                lng: store.geospatial.lon,
              },
              map: self.radar,
              title: store.name,
            })
            console.log(storeMaker)
          })
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
