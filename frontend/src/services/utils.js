import axios from 'axios'

export default class {
  static getAjaxInstance() {
    const instance = axios.create({
      baseURL: '127.0.0.1:5000/api/',
    })
    return instance
  }
}
