import { renderCurrentCrib } from "./start.js";

export function displayScoredHand(player) {
  let playerCardsArea = $('#' + player + '-cards');
  let playerCards = $(playerCardsArea).children();
  $.each(playerCards, function(index, playerCard) {
    $(playerCard).removeClass('played').addClass('scored');
    playerCardsArea.append(playerCard);
  });
}

export function awardPoints(player, amount, reason) {
  let playerPoints = $("#scoreboard-" + player + "-points");
  $(playerPoints).animate({color: '#7FFF00'}, 500);
  $(playerPoints).animate({color: 'white)'}, 1000);

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
