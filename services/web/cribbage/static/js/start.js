function renderDealerIcon(nickname) {
  // given the name of the current dealer, append an icon next to their name, and activate the deal button for that player
  $("#" + nickname).find(".player-nickname").prepend('<span class="dealer-icon fas fa-star"></span>');
  $("#" + nickname + " #action-button").prop('disabled', false);
}

export function start(msg) {
  console.log('started with players: ' + msg.players);
  sessionStorage.setItem('players', JSON.stringify(msg.players));
  let players = JSON.parse(sessionStorage.getItem('players'));
  let dealer = players[0];
  console.log('crib belongs to '+ dealer);
  $('#action-button').html('Deal').prop('disabled', true);
  renderDealerIcon(dealer);
}