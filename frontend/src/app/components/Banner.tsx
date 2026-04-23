'use client';
import { useEffect, useState } from 'react';
import './banner.css';

import img0 from '../assets/carousel_0.png';
import img1 from '../assets/carousel_1.png';
import img2 from '../assets/carousel_2.png';
import img3 from '../assets/carousel_3.png';
import img4 from '../assets/carousel_4.jpg';
import img5 from '../assets/carousel_5.jpg';
import img6 from '../assets/carousel_6.jpg';
import img7 from '../assets/carousel_7.jpg';
import img8 from '../assets/carousel_8.jpg';

const images = [
  img0.src,
  img1.src,
  img2.src,
  img3.src,
  img4.src,
  img5.src,
  img6.src,
  img7.src,
  img8.src,
];

export default function Banner() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % images.length);
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="banner">
      {images.map((img, i) => (
        <div
          key={i}
          className={`banner-image ${i === index ? 'active' : ''}`}
          style={{
            backgroundImage: `
              linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.2)),
              url(${img})
            `,
          }}
        />
      ))}

      <div className="text">
        <h1>Make Your Mark</h1>
        <h4>Create and sign petitions.</h4>
        <h4>Receive official responses from Student Government.</h4>
      </div>
    </div>
  );
}
