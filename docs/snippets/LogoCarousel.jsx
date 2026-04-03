{/*
  LogoCarousel component for the Agent Skills documentation.
  Shuffles clients on each page load for fair exposure.
*/}
export const LogoCarousel = ({clients}) => {

  /* Shuffle clients on component mount */
  const [shuffled, setShuffled] = useState(clients);

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

  const Logo = ({ client }) => (
    <a href={client.url} className="block no-underline border-none w-full h-full">
      <img className="block dark:hidden object-contain w-full h-full !my-0" src={client.lightSrc} alt={client.name} noZoom />
      <img className="hidden dark:block object-contain w-full h-full !my-0" src={client.darkSrc} alt={client.name} noZoom />
    </a>
  );

  const row1 = shuffled.filter((_, i) => i % 2 === 0);
  const row2 = shuffled.filter((_, i) => i % 2 === 1);
  const row1Doubled = [...row1, ...row1];
  const row2Doubled = [...row2, ...row2];

  return (
    <>
      <div className="logo-carousel">
        <div className="logo-carousel-track" style={{ animation: 'logo-scroll 50s linear infinite' }}>
          {row1Doubled.map((client, i) => (
            <div key={`${client.name}-${i}`} style={{ width: 150 * (client.scale || 1), maxWidth: "100%" }}>
              <Logo client={client} />
            </div>
          ))}
        </div>
      </div>
      <div className="logo-carousel">
        <div className="logo-carousel-track" style={{ animation: 'logo-scroll 60s linear infinite reverse' }}>
          {row2Doubled.map((client, i) => (
            <div key={`${client.name}-${i}`} style={{ width: 150 * (client.scale || 1), maxWidth: "100%" }}>
              <Logo client={client} />
            </div>
          ))}
        </div>
      </div>
    </>
  );
};
