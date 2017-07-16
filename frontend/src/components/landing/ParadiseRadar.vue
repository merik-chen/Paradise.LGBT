<template lang='pug'>
  div
    #searchMore(v-if='searchMore==true')
      a(@click='searchStores') 搜尋更多
    #radar
</template>

<script>
import { StoreService } from '@/services/index'

const loadGoogleMapsAPI = require('load-google-maps-api')

const storeService = new StoreService()

export default {
  data() {
    const initData = {
      googleMaps: null,
      radar: null,
      marker: null,
      storeList: null,
      currentPosition: null,
      searchMore: false,
      storeMarkers: [],
    }

    return initData
  },
  watch: {
    /*
     * 位置改變後更新/初始地圖
     */
    currentPosition() {
      if (this.radar) {
        this.updatePosition()
      } else {
        this.initRadar()
      }
    },
  },
  methods: {
    getUserGeoInfo() {
      const self = this
      if ('geolocation' in navigator) {
        navigator.geolocation.watchPosition((position) => {
          self.currentPosition = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          }
        }, () => {
          alert('無法取得您的地理位置')
        })
      }
    },
    async searchStores() {
      const self = this
      self.searchMore = false
      const image = {
        url: 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png',
        // This marker is 20 pixels wide by 32 pixels high.
        size: new self.googleMaps.Size(20, 32),
      }
      const { lat, lng } = this.currentPosition
      self.removeStores()
      const storesData = await storeService.searchByGeo(lat, lng)
      self.storeList = storesData.stores
      self.storeList.forEach((store) => {
        const storeMarker = new self.googleMaps.Marker({
          position: {
            lat: store.geospatial.lat,
            lng: store.geospatial.lon,
          },
          map: self.radar,
          title: store.name,
          icon: image,
        })
        self.storeMarkers.push(storeMarker)
      })
    },
    initRadar() {
      const self = this
      const center = {
        ...self.currentPosition,
      }
      self.radar = new self.googleMaps.Map(
      document.getElementById('radar'), {
        center,
        zoom: 19,
      })
      self.marker = new self.googleMaps.Marker({
        position: center,
        map: self.radar,
        animation: self.googleMaps.Animation.DROP,
      })
      self.searchStores()
    },
    updatePosition() {
      const self = this
      const center = new self.googleMaps.LatLng(self.currentPosition.lat, self.currentPosition.lng)
      self.searchMore = true
      self.radar.panTo(center)
      self.marker.setPosition(center)
    },
    removeStores() {
      const self = this
      self.storeMarkers.forEach((marker) => {
        marker.setMap(null)
      })
      self.storeMarker = []
      self.storeList = null
    },
  },
  created() {
    const self = this
    loadGoogleMapsAPI({
      key: 'AIzaSyDFBy8_iLrMYSfTF5py7plQXBXilhYlt5Y',
    }).then((googleMaps) => {
      self.googleMaps = googleMaps
      self.getUserGeoInfo()
    })
  },
}
</script>

<style lang="sass" scoped>
  #radar
    width: 100%
    height: 100%
  #searchMore
    position: absolute
    top: 20px
    left: 50%
    transform: translateX(-50%)
    z-index: 10
    padding: 10px
    background: #fff
    box-shadow: 1px 1px 1px #afafaf
    cursor: pointer
    color: #292929
</style>
