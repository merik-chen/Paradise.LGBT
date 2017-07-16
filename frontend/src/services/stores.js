import Utils from './utils'

export default class StoreService {
  constructor() {
    this.ajax = Utils.getAjaxInstance()
  }

  async searchByGeo(lat, lng, radius = 500, unit = 'm', page = 1) {
    const url = `nearBy/${lng}/${lat}/${radius}/${unit}/${page}`
    const returnData = await this.ajax.get(url)
    const jsonObject = Utils.toJSONAPIObject(returnData.data)
    return jsonObject
  }
}
