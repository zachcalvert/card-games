import {renderCurrentTurnDisplay} from "./peg.js";

export function renderDealerIcon(dealer) {
  $('.dealer-icon').remove();
  $("#" + dealer).find(".player-nickname").prepend('<span class="dealer-icon fas fa-star"></span>');
}

export function resetTable() {
  $('.player-card').remove();
  $('.opponent-card').remove();
  $('.crib-card').remove();
  $('.cut-card').remove();
  $('.player-points').text(0);
  $('#play-total').text('');
}

export function start(dealer) {
  renderCurrentTurnDisplay(dealer, 'DEAL');
  renderDealerIcon(dealer);
}