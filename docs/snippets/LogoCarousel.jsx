{/*
  LogoCarousel component for the Agent Skills documentation.
  Shuffles clients on each page load for fair exposure.
*/}
export const LogoCarousel = ({clients}) => {
  const [shuffled, setShuffled] = useState(clients);

  /* Shuffle clients on component mount */
  useEffect(() => {
    const shuffle = (items) => {
      const copy = [...items];
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
      return copy;
    };
    setShuffled(shuffle(clients));
  }, []);

  const doubled = [...shuffled, ...shuffled];

  const GAP_PX = 48; // 3rem at the default 16px base
  const PX_PER_SECOND = 40;
  const cycleWidth = shuffled.reduce(
    (sum, client) => sum + 150 * (client.scale || 1) + GAP_PX,
    0,
  );
  const cycleDuration = cycleWidth / PX_PER_SECOND;

  const Logo = ({ client }) => (
    <a href={client.url} className="block no-underline border-none w-full h-full">
      <img className="block dark:hidden object-contain w-full h-full !my-0" src={client.lightSrc} alt={client.name} noZoom />
      <img className="hidden dark:block object-contain w-full h-full !my-0" src={client.darkSrc} alt={client.name} noZoom />
    </a>
  );

  return (
    <div className="logo-carousel">
      <div className="logo-carousel-track" style={{ animation: `logo-scroll ${cycleDuration}s linear infinite` }}>
        {doubled.map((client, i) => (
          <div key={`${client.name}-${i}`} style={{ width: 150 * (client.scale || 1), maxWidth: "100%" }}>
            <Logo client={client} />
          </div>
        ))}
      </div>
    </div>
  );
};
