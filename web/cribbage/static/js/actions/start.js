import {renderCurrentTurnDisplay} from "./peg.js";

export function renderDealerIcon(dealer) {
  $('.dealer-icon').remove();
  $("#" + dealer).find(".player-nickname").append('<button class="btn btn-outline-light btn-sm disabled">CRIB</button>');
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
  renderDealerIcon(dealer);
  renderCurrentTurnDisplay(dealer, 'DEAL');
}