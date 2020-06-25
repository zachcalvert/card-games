import { renderCurrentTurnDisplay } from "./peg.js";

export function renderCurrentCrib(dealer) {
  $('.crib').find('.panel-heading').text(dealer + "'s crib");
}

function buildScoreBoard(players) {
  console.log('building scoreboard for players: ' + players);
  let table = $('<table>').addClass('table table-striped table-dark table-responsive');

  let thead = $('<thead>');
  thead.append('<tr>');

  let tbody = $('<tbody>');
  tbody.append('<tr>');

  $.each(players, function(index, player) {
    let nameCell = $('<td/>', {
      id: 'scoreboard-' + player + '-name',
      html: player
    });
    thead.find('tr').append(nameCell);

    let pointsCell = $('<td/>', {
      id: 'scoreboard-' + player + '-points',
      html: 0
    });
    tbody.find('tr').append(pointsCell);
  });

  table.append(thead);
  table.append(tbody);
  $('.scoreboard').append(table);
}

export function resetTable() {
  $('.player-card').remove();
  $('.opponent-card').remove();
  $('.crib-card').remove();
  $('.cut-card').remove();
  $('.player-points').text(0);
  $('#play-total').text('');
}

export function start(dealer, players) {
  buildScoreBoard(players);
  renderCurrentCrib(dealer);
  renderCurrentTurnDisplay(dealer, 'DEAL');
}