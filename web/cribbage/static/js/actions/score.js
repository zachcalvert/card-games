import { renderCurrentCrib } from "./start.js";

export function displayScoredHand(player) {
  let playerCards = $('.player-card');
  let playerCardsArea = $('#' + player + '-cards');
  $.each(playerCards, function(index, playerCard) {
      playerCardsArea.append(playerCard);
  });
  playerCards.removeClass('played');
}

export function awardPoints(player, amount, reason) {
  let playerHeader = $("#" + player).find(".player-points");
  $(playerHeader).animate({color: '#7FFF00'}, 500);
  $(playerHeader).animate({color: 'white)'}, 1000);

  let playerPoints = $("#" + player).find(".player-points");
  let current = parseInt(playerPoints.text());
  $({someValue: current}).animate({someValue: current + amount}, {
      duration: 200,
      easing:'swing',
      step: function() {
          $(playerPoints).text(Math.round(this.someValue));
      }
  });
}

export function revealCrib() {
  let cribCards = $('.crib-card');
  $.each(cribCards, function(index, cribCard) {
    $(cribCard).attr("src",'/static/img/cards/' + cribCard.id);
  });
}

export function clearTable(next_dealer) {
  $('.player-card').remove();
  $('.opponent-card').remove();
  $('.crib-card').remove();
  $('.cut-card').remove();
  $('#play-total').text('');
  renderCurrentCrib(next_dealer);
}
