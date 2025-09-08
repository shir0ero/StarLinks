// Configuration
const API_BASE_URL = 'http://localhost:5001';
let selectedActor = null;
let selectedSecondActor = null;

// DOM Elements
const mainSearchInput = document.getElementById('mainSearchInput');
const searchSuggestions = document.getElementById('searchSuggestions');
const actionButtons = document.getElementById('actionButtons');
const selectedActorDiv = document.getElementById('selectedActor');
const loadingSpinner = document.getElementById('loadingSpinner');

// Feature sections
const knowAboutSection = document.getElementById('knowAboutSection');
const degreeSeparationSection = document.getElementById('degreeSeparationSection');
const socialLinksSection = document.getElementById('socialLinksSection');

// Initialize the app
document.addEventListener('DOMContentLoaded', function () {
  initializeEventListeners();
});

function initializeEventListeners() {
  // Main search input
  mainSearchInput.addEventListener('input', handleMainSearch);
  mainSearchInput.addEventListener('blur', () => {
    setTimeout(() => hideSuggestions('searchSuggestions'), 150);
  });
  mainSearchInput.addEventListener('focus', () => {
    if (mainSearchInput.value.trim()) handleMainSearch();
  });

  // Action buttons
  document.getElementById('knowAboutBtn').addEventListener('click', showKnowAbout);
  document.getElementById('degreeSeparationBtn').addEventListener('click', showDegreeSeparation);
  document.getElementById('socialLinksBtn').addEventListener('click', showSocialLinks);
  document.getElementById('resetBtn').addEventListener('click', resetSearch);

  // Second actor search for degrees of separation
  const secondActorInput = document.getElementById('secondActorInput');
  secondActorInput.addEventListener('input', handleSecondActorSearch);
  secondActorInput.addEventListener('blur', () => {
    setTimeout(() => hideSuggestions('secondActorSuggestions'), 150);
  });
  secondActorInput.addEventListener('focus', () => {
    if (secondActorInput.value.trim()) handleSecondActorSearch();
  });
}

// Search functionality
async function handleMainSearch() {
  const query = mainSearchInput.value.trim();
  if (query.length < 2) {
    hideSuggestions('searchSuggestions');
    return;
  }
  try {
    const response = await fetch(`${API_BASE_URL}/find_actors?name=${encodeURIComponent(query.toLowerCase())}`);
    const actors = await response.json();
    if (Array.isArray(actors) && actors.length > 0) {
      displaySuggestions(actors, 'searchSuggestions', selectMainActor);
    } else {
      hideSuggestions('searchSuggestions');
    }
  } catch (error) {
    console.error('Error fetching actors:', error);
    hideSuggestions('searchSuggestions');
  }
}

async function handleSecondActorSearch() {
  const query = document.getElementById('secondActorInput').value.trim();
  if (query.length < 2) {
    hideSuggestions('secondActorSuggestions');
    return;
  }
  try {
    const response = await fetch(`${API_BASE_URL}/find_actors?name=${encodeURIComponent(query.toLowerCase())}`);
    const actors = await response.json();
    if (Array.isArray(actors) && actors.length > 0) {
      displaySuggestions(actors, 'secondActorSuggestions', selectSecondActor);
    } else {
      hideSuggestions('secondActorSuggestions');
    }
  } catch (error) {
    console.error('Error fetching actors:', error);
    hideSuggestions('secondActorSuggestions');
  }
}

function displaySuggestions(actors, containerId, selectCallback) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  actors.slice(0, 5).forEach((actor) => {
    const item = document.createElement('div');
    item.className = 'suggestion-item';
    item.innerHTML = `
      <div class="suggestion-info">
        <div class="suggestion-name">${actor.name}</div>
        <div class="suggestion-birth">Born: ${actor.birth || 'Unknown'}</div>
      </div>
    `;
    item.addEventListener('click', () => selectCallback(actor));
    container.appendChild(item);
  });
  showSuggestions(containerId);
}

function showSuggestions(containerId) {
  document.getElementById(containerId).classList.add('show');
}
function hideSuggestions(containerId) {
  document.getElementById(containerId).classList.remove('show');
}

function selectMainActor(actor) {
  selectedActor = actor;
  mainSearchInput.value = actor.name;
  hideSuggestions('searchSuggestions');
  showActionButtons();
}

function selectSecondActor(actor) {
  selectedSecondActor = actor;
  document.getElementById('secondActorInput').value = actor.name;
  hideSuggestions('secondActorSuggestions');
  findConnection();
}

function showActionButtons() {
  selectedActorDiv.innerHTML = `
    <h3>${selectedActor.name}</h3>
    <p>Born: ${selectedActor.birth || 'Unknown'}</p>
  `;
  actionButtons.style.display = 'block';
  actionButtons.scrollIntoView({ behavior: 'smooth' });
}

function resetSearch() {
  selectedActor = null;
  selectedSecondActor = null;
  mainSearchInput.value = '';
  document.getElementById('secondActorInput').value = '';
  actionButtons.style.display = 'none';
  hideAllSections();
  mainSearchInput.focus();
}

function hideAllSections() {
  knowAboutSection.style.display = 'none';
  degreeSeparationSection.style.display = 'none';
  socialLinksSection.style.display = 'none';
}
function closeSection(sectionId) {
  document.getElementById(sectionId).style.display = 'none';
}

// Feature implementations
async function showKnowAbout() {
  if (!selectedActor) return;
  hideAllSections();
  showLoading();
  try {
    const response = await fetch(`${API_BASE_URL}/actor_profile/${selectedActor.id}`);
    const profileData = await response.json();
    displayActorProfile(profileData);
    knowAboutSection.style.display = 'block';
    knowAboutSection.scrollIntoView({ behavior: 'smooth' });
  } catch (error) {
    console.error('Error fetching actor profile:', error);
    alert('Error loading actor profile. Please try again.');
  } finally {
    hideLoading();
  }
}

function displayActorProfile(data) {
  const profileContainer = document.getElementById('actorProfile');
  const profile = data?.profile || {};
  const imageUrl = profile.profile_path
    ? `https://image.tmdb.org/t/p/w300${profile.profile_path}`
    : 'https://via.placeholder.com/300x450?text=No+Image';
  profileContainer.innerHTML = `
    <div class="profile-image">
      <img src="${imageUrl}" alt="${profile.name || 'Actor'}" onerror="this.src='https://via.placeholder.com/300x450?text=No+Image'">
    </div>
    <div class="profile-details">
      <div class="detail-card">
        <h3><i class="fas fa-user"></i> Personal Info</h3>
        <p><strong>Full Name:</strong> ${profile.name || 'Unknown'}</p>
        <p><strong>Birthday:</strong> ${profile.birthday || 'Unknown'}</p>
        <p><strong>Place of Birth:</strong> ${profile.place_of_birth || 'Unknown'}</p>
        ${profile.deathday ? `<p><strong>Death:</strong> ${profile.deathday}</p>` : ''}
      </div>
      <div class="detail-card">
        <h3><i class="fas fa-book"></i> Biography</h3>
        <p>${profile.biography || 'No biography available.'}</p>
      </div>
      ${
        data?.charts
          ? `
        <div class="detail-card">
          <h3><i class="fas fa-chart-line"></i> Career Stats</h3>
          <p><strong>Total Movies:</strong> ${data.charts.ratings_over_time.labels.length}</p>
          <p><strong>Career Span:</strong> ${data.charts.movies_per_year.labels[0]} - ${
              data.charts.movies_per_year.labels[data.charts.movies_per_year.labels.length - 1]
            }</p>
        </div>
      `
          : ''
      }
    </div>
  `;
}

async function showDegreeSeparation() {
  if (!selectedActor) return;
  hideAllSections();
  // Prepare UI
  document.getElementById('firstActorName').textContent = selectedActor.name;
  document.getElementById('firstActorBirth').textContent = `Born: ${selectedActor.birth || 'Unknown'}`;
  document.getElementById('secondActorInput').value = '';
  document.getElementById('connectionResults').innerHTML = '';
  document.getElementById('networkVisualization').innerHTML = '';
  selectedSecondActor = null;
  degreeSeparationSection.style.display = 'block';
  degreeSeparationSection.scrollIntoView({ behavior: 'smooth' });
}

async function findConnection() {
  if (!selectedActor || !selectedSecondActor) return;
  showLoading();
  try {
    // 1) Path
    const pathResponse = await fetch(`${API_BASE_URL}/path_by_id`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_id: selectedActor.id.toString(),
        target_id: selectedSecondActor.id.toString(),
      }),
    });
    const pathData = await pathResponse.json();
    if (pathData?.error) {
      displayConnectionResults(pathData);
      return;
    }
    displayConnectionResults(pathData);

    // 2) Network (non-blocking)
    try {
      const networkResponse = await fetch(`${API_BASE_URL}/network`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actor_ids: [selectedActor.id.toString(), selectedSecondActor.id.toString()],
        }),
      });
      const networkData = await networkResponse.json();
      if (networkData && Array.isArray(networkData.nodes)) {
        displayNetworkVisualization(networkData);
      } else {
        // Optional: notice
        // document.getElementById('networkVisualization').innerHTML = '<p>Network graph unavailable.</p>';
      }
    } catch (netErr) {
      console.warn('Network subgraph fetch failed:', netErr);
      // document.getElementById('networkVisualization').innerHTML = '<p>Network graph unavailable.</p>';
    }
  } catch (error) {
    console.error('Error finding connection:', error);
    document.getElementById('connectionResults').innerHTML = `
      <div class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        Error finding connection. Please try again.
      </div>
    `;
  } finally {
    hideLoading();
  }
}

function displayConnectionResults(data) {
  const resultsContainer = document.getElementById('connectionResults');
  if (!data || data.error) {
    resultsContainer.innerHTML = `
      <div class="no-connection">
        <i class="fas fa-unlink"></i>
        <h3>No Connection Found</h3>
        <p>These actors are not connected through shared movies in our database.</p>
      </div>
    `;
    return;
  }
  const degrees = typeof data.degrees === 'number' ? data.degrees : 0;
  const path = Array.isArray(data.path) ? data.path : [];
  let html = `
    <div class="connection-header">
      <h3><i class="fas fa-link"></i> ${degrees} Degree${degrees !== 1 ? 's' : ''} of Separation</h3>
    </div>
    <div class="connection-path">
  `;
  path.forEach((step) => {
    html += `
      <div class="connection-step">
        <div class="step-actors">
          <span class="step-actor">${step.person1}</span>
          <span class="step-actor">${step.person2}</span>
        </div>
        <div class="step-movies">
          <i class="fas fa-film"></i>
          ${Array.isArray(step.movies) && step.movies.length ? step.movies.join(', ') : 'No shared titles recorded'}
        </div>
      </div>
    `;
  });
  html += '</div>';
  resultsContainer.innerHTML = html;
}

function displayNetworkVisualization(data) {
  const container = document.getElementById('networkVisualization');

  // Normalize nodes (ensure string ids)
  const rawNodes = Array.isArray(data?.nodes) ? data.nodes : [];
  const nodes = rawNodes.map((n) => ({
    ...n,
    id: (n.id ?? n.Id ?? n.ID)?.toString(),
  }));

  // Normalize edges from {from,to} or {source,target} to {source,target} strings
  const rawEdges = Array.isArray(data?.edges) ? data.edges : [];
  const edges = rawEdges
    .map((e) => ({
      source: (e.source ?? e.from ?? e.Source ?? e.FROM)?.toString(),
      target: (e.target ?? e.to ?? e.Target ?? e.TO)?.toString(),
      title: e.title || '',
    }))
    .filter((e) => e.source && e.target);

  if (!nodes.length || !edges.length) {
    console.warn('Network missing nodes/edges', { nodes, edges, raw: data });
    container.innerHTML = '<p>No network data available.</p>';
    return;
  }

  container.innerHTML = '<svg id="network-svg"></svg>';
  const svg = d3.select('#network-svg');

  const computedWidth = container.clientWidth || container.getBoundingClientRect().width || 600;
  const width = Math.max(320, Math.floor(computedWidth));
  const height = 420;

  svg.attr('width', width).attr('height', height);

  const simulation = d3
    .forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id((d) => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));

  const link = svg
    .append('g')
    .selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', 2);

  const node = svg
    .append('g')
    .selectAll('circle')
    .data(nodes)
    .enter()
    .append('circle')
    .attr('r', (d) => d.size || 15)
    .attr('fill', (d) => d.color || '#667eea')
    .call(
      d3
        .drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended)
    );

  const label = svg
    .append('g')
    .selectAll('text')
    .data(nodes)
    .enter()
    .append('text')
    .text((d) => d.label)
    .attr('font-size', '12px')
    .attr('fill', '#333')
    .attr('text-anchor', 'middle')
    .attr('dy', -20);

  simulation.on('tick', () => {
    link
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y);

    node.attr('cx', (d) => d.x).attr('cy', (d) => d.y);
    label.attr('x', (d) => d.x).attr('y', (d) => d.y);
  });

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}

async function showSocialLinks() {
  if (!selectedActor) return;
  hideAllSections();
  showLoading();
  try {
    const response = await fetch(`${API_BASE_URL}/actor_social/${selectedActor.id}`);
    let socialData;
    if (response.ok) {
      socialData = await response.json();
    } else {
      socialData = generateMockSocialLinks();
    }
    displaySocialLinks(socialData);
    socialLinksSection.style.display = 'block';
    socialLinksSection.scrollIntoView({ behavior: 'smooth' });
  } catch (error) {
    console.error('Error fetching social links:', error);
    displaySocialLinks(generateMockSocialLinks());
    socialLinksSection.style.display = 'block';
    socialLinksSection.scrollIntoView({ behavior: 'smooth' });
  } finally {
    hideLoading();
  }
}

function generateMockSocialLinks() {
  const actorName = selectedActor.name.toLowerCase().replace(/\s+/g, '');
  return {
    links: [
      {
        platform: 'Instagram',
        icon: 'fab fa-instagram',
        username: `@${actorName}`,
        url: `https://instagram.com/${actorName}`,
        verified: true,
      },
      {
        platform: 'Twitter',
        icon: 'fab fa-twitter',
        username: `@${actorName}`,
        url: `https://twitter.com/${actorName}`,
        verified: true,
      },
      {
        platform: 'IMDb',
        icon: 'fab fa-imdb',
        username: selectedActor.name,
        url: `https://imdb.com/name/nm${selectedActor.id}`,
        verified: true,
      },
      {
        platform: 'Wikipedia',
        icon: 'fab fa-wikipedia-w',
        username: selectedActor.name,
        url: `https://wikipedia.org/wiki/${selectedActor.name.replace(/\s+/g, '_')}`,
        verified: false,
      },
    ],
  };
}

function displaySocialLinks(data) {
  const container = document.getElementById('socialLinksContent');
  if (!data.links || data.links.length === 0) {
    container.innerHTML = `
      <div class="no-social-links">
        <i class="fas fa-share-alt"></i>
        <h3>No Social Links Available</h3>
        <p>We couldn't find verified social media accounts for this actor.</p>
      </div>
    `;
    return;
  }
  let html = '<div class="social-links-grid">';
  data.links.forEach((link) => {
    html += `
      <a href="${link.url}" target="_blank" class="social-link-card">
        <div class="social-platform">
          <i class="${link.icon}"></i>
          <span>${link.platform}</span>
          ${link.verified ? '<i class="fas fa-check-circle" style="color: #1da1f2; margin-left: 5px;"></i>' : ''}
        </div>
        <div class="social-username">${link.username}</div>
      </a>
    `;
  });
  html += '</div>';
  container.innerHTML = html;
}

function showLoading() {
  loadingSpinner.style.display = 'flex';
}
function hideLoading() {
  loadingSpinner.style.display = 'none';
}
