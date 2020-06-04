const namespace = '/game';
const socket = io(namespace);
const gameName = sessionStorage.getItem('gameName');
const nickname = sessionStorage.getItem('nickname');


export function renderCurrentTurnDisplay(player) {
  // given the name of who's turn it currently is, append an icon next to their name
  $("#" + player).find(".panel-heading").css('background', 'pink');
}

export function removeCurrentTurnDisplay(player) {
  // given the name of who's turn it currently is, append an icon next to their name
  $("#" + player).find(".panel-heading").css('background', 'rgb(21, 32, 43)');
}

// export function rotateTurn(player_order, current_player) {
//   console.log('player_order is ' + player_order);
//   console.log('current_player is ' + current_player);
//   removeCurrentTurnDisplay(current_player);
//
//   let next_player = PLAYER_ORDER[PLAYER_ORDER.indexOf(current_player) +1];
//   if (!next_player) {
//     next_player = PLAYER_ORDER[0];
//   }
//   console.log('next player is ' + next_player);
//
//   renderCurrentTurnDisplay(next_player);
//   return next_player;
// }

