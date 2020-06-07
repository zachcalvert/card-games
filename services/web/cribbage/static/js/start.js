function renderDealerIcon(dealer) {
  // given the name of the current dealer, append an icon next to their name, and activate the deal button for that player
  $("#" + dealer).find(".player-nickname").prepend('<span class="dealer-icon fas fa-star"></span>');
  $("#" + dealer + " #action-button").prop('disabled', false);
}

export function start(dealer) {
  $('#action-button').html('Deal').prop('disabled', true);
  renderDealerIcon(dealer);
}