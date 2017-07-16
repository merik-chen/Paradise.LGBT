<template lang='pug'>
  div
    #searchMore(v-show='searchMore==true')
      a(@click='searchStores' href='#') 搜尋更多
    ul.controlPanel
      li 
        a(
          v-show='watchID > 0' 
          @click='stopWatchPosition'
          href='#'
        ) 停止自動更新位置
        a(
          v-show='!!watchID == false' 
          @click='getUserGeoInfo'
          href='#'
        ) 自動更新位置
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
      previousPosition: null,
      shouldUpdatePrePosition: true,
      searchMore: false,
      storeMarkers: [],
      watchID: null,
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
        self.watchID = navigator.geolocation.watchPosition((position) => {
          if (self.shouldUpdatePrePosition === true && self.currentPosition) {
            self.previousPosition = self.currentPosition
            self.shouldUpdatePrePosition = false
          }
          self.currentPosition = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          }
        }, () => {
          alert('無法取得您的地理位置')
        })
      }
    },
    stopWatchPosition() {
      navigator.geolocation.clearWatch(this.watchID)
      this.watchID = null
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
        zoom: 18,
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
      const previousLatLng =
        new self.googleMaps.LatLng(self.previousPosition.lat, self.previousPosition.lng)
      const distance =
        self.googleMaps.geometry.spherical.computeDistanceBetween(center, previousLatLng)
      self.shouldUpdatePrePosition = false
      // 距離大於50m 允許重新搜尋店家
      if (distance > 250) {
        self.shouldUpdatePrePosition = true
        self.searchMore = true
      }
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
      libraries: ['geometry'],
    }).then((googleMaps) => {
      self.googleMaps = googleMaps
      self.getUserGeoInfo()
    })
  },
}
</script>

<style lang="sass" scoped>
  a
    text-decoration: none
    color: #292929
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
  .controlPanel
    position: absolute
    bottom: 20px
    right: 100px
    z-index: 10
    background: #fff
    box-shadow: 1px 1px 1px #afafaf
    list-style-type: none
    padding: 0
    li
      padding: 5px
</style>
