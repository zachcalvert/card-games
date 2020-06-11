import {renderCurrentTurnDisplay} from "./peg.js";

export function renderDealerIcon(dealer) {
  $('.dealer-icon').remove();
  $("#" + dealer).find(".player-nickname").prepend('<span class="dealer-icon fas fa-star"></span>');
}

function renderDeck() {
  let deckImage = $('<img/>', {
    id: 'deck',
    src: '/static/img/cards/facedown.png'
  });
  $('#deck-area').append(deckImage);
}

export function resetTable() {
  $('.playedOpponentCard').remove();
  $('.cribCard').remove();
  $('.cutCard').remove();
  $('.playerCard').remove();
  $('.player-points').text(0);
  $('#play-total').text(0);
}

export function start(dealer) {
  renderCurrentTurnDisplay(dealer, 'DEAL');
  renderDealerIcon(dealer);
}