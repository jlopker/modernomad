import React, {PropTypes} from 'react'
import { browserHistory } from 'react-router'
import RoomIndex from './RoomIndex'

const hardcodedRooms = [
  {id: 1, name: "Lovelace", cost:"150", type:"Private Room", guests:"2", img: ["/media/rooms/82c1da3f-67d2-443e-850f-c76a3639e063.png", "/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 2, name: "Flyut", cost:"55", type: "Shared Room", guests:"1", img: ["/media/rooms/ed6e58fa-df9f-4e94-848e-7f402516421e.png", "/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 3, name: "Fishbowl", cost:"100", type: "Shared Room", guests:"3", img: ["/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png"]},
  {id: 4, name: "Golden Age", cost:"110", type: "Shared Room", guests:"4", img: ["/media/rooms/53bf31a8-2afa-4e6e-94e2-3ecb5dc2d3bd.png", "/media/rooms/ed6e58fa-df9f-4e94-848e-7f402516421e.png"]},
]

export default class RoomContainer extends React.Component {
  constructor(props) {
    super(props)

    this.state = {rooms: hardcodedRooms}
  }

  reFilter(filters) {
    this.setState({rooms: []})
    const formattedDates = {arrive: filters.dates.arrive.format('MM/DD/YYYY'), depart: filters.dates.depart.format('MM/DD/YYYY')}
    browserHistory.push({
      pathname: '/locations/'+this.props.routeParams.location+'/stay',
      query: formattedDates
    })
  }

  render() {
    return <RoomIndex
      rooms={this.state.rooms}
      routeParams={this.props.routeParams}
      query={this.props.location.query}
      onFilterChange={this.reFilter.bind(this)} />
  }
}
