import {renderDealerIcon} from "./start.js";

export function awardPoints(player, amount, reason) {
  console.log('awarding ' + amount + 'points to ' + player + ' for ' + reason);
  let playerPoints = $("#" + player).find(".player-points");
  let current = parseInt(playerPoints.text());
  playerPoints.css('color', 'green');
  $({someValue: current}).animate({someValue: current + amount}, {
      duration: 200,
      easing:'swing',
      step: function() {
          $(playerPoints).text(Math.round(this.someValue));
          $(playerPoints).css('color', 'white');
      }
  });
}

export function revealCrib() {
  let cribCards = $('.cribCard');
  $.each(cribCards, function(index, cribCard) {
    $(cribCard).attr("src",'/static/img/cards/' + cribCard.id);
  });
}

export function clearTable(next_dealer) {
  $('.playedOpponentCard').remove();
  $('.cribCard').remove();
  $('.cutCard').remove();
  $('.playerCard').remove();
  renderDealerIcon(next_dealer);
}