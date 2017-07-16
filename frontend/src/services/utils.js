import axios from 'axios'
import JSONAPISerializer from 'jsonapi-serializer'

export default class {
  static getAjaxInstance() {
    const instance = axios.create({
      baseURL: '/api/',
    })
    return instance
  }

  static toJSONAPIObject(jsonapi) {
    const JSONAPIDeserializer = JSONAPISerializer.Deserializer
    const object = new JSONAPIDeserializer().deserialize(jsonapi, (err, data) => data)

    return object
  }
}
