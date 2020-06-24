import { renderCurrentTurnDisplay } from "./peg.js";

export function renderCurrentCrib(dealer) {
  $('.crib').find('.panel-heading').text(dealer + "'s crib");
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
  renderCurrentCrib(dealer);
  renderCurrentTurnDisplay(dealer, 'DEAL');
}