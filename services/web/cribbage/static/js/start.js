function renderDealerIcon(nickname) {
  // given the name of the current dealer, append an icon next to their name, and activate the deal button for that player
  $("#" + nickname).find(".player-nickname").prepend('<span class="dealer-icon fas fa-star"></span>');
  $("#" + nickname + " #action-button").prop('disabled', false);
}

export function start(dealer) {
  $('#action-button').html('Deal').prop('disabled', true);
  renderDealerIcon(dealer);
}