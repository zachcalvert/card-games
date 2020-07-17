export function displayScoredHand(player) {
  let playerCardsArea = $('#' + player + '-cards');
  let playerCards = $(playerCardsArea).children();
  $.each(playerCards, function(index, playerCard) {
    $(playerCard).removeClass('played').addClass('scored');
    playerCardsArea.append(playerCard);
  });
}

export function awardPoints(team, amount, reason) {
  let winningScore = sessionStorage.getItem('ws');
  let playerPoints = $("#scoreboard-" + team + "-points");
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

  let totalPoints = current + amount;
  let width = (totalPoints / winningScore * 100) + '%';
  $('#' + player + '-player-progress-bar').css('width', width).text(totalPoints);
}

export function clearTable(next_dealer) {
  $('.card').remove();
}