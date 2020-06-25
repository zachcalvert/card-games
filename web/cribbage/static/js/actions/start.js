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


  // $('.scoreboard').find('table').find('thead tr').append( $('<th />', {text : 'zeke'}) )
 // <table class="table table-striped table-dark">
 //    <thead>
 //      <tr>
 //        <td id="scoreboard-{{ player_name }}-name">{{ player_name}}</td>
 //        {% for name, points in opponents.items() %}
 //          <td id="scoreboard-{{ name }}-name">{{ name }}</td>
 //        {% endfor %}
 //        </tr>
 //    </thead>
 //    <tbody>
 //      <tr>
 //        <td id="scoreboard-{{ player_name }}-points">{{ player_points }}</td>
 //        {% for name, points in opponents.items() %}
 //          <td id="scoreboard-{{ name }}-points">{{ points }}</td>
 //        {% endfor %}
 //      </tr>
 //    </tbody>
 //  </table>
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