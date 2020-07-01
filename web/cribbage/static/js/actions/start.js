import { renderCurrentTurnDisplay } from "./peg.js";

export function renderCurrentCrib(dealer) {
  $('.crib').find('.panel-heading').text(dealer + "'s crib");
}

function buildScoreBoard(players) {


  $.each(players, function(index, player) {
    let points = $('<span/>', {
      id: 'scoreboard-' + player + '-points',
      html: 0
    });
    let playerName = $('#' + player).find('.player-nickname');
    playerName.append(': ');
    playerName.append(points);
  });
}

export function resetTable() {
  $('.player-card').remove();
  $('.opponent-card').remove();
  $('.crib-card').remove();
  $('.cut-card').remove();
  $('.scoreboard').remove();
  $('.winner').remove();
  $('#play-total').text('');
}

export function start(dealer, players) {
  buildScoreBoard(players);
  renderCurrentCrib(dealer);
  renderCurrentTurnDisplay(dealer, 'DEAL');
}